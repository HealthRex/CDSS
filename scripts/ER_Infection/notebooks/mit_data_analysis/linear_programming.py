from pulp import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white', font_scale=1.5)
from pulp.apis import PULP_CBC_CMD
import os
from tqdm import tqdm

import pdb

class AbxDecisionMaker():

    def __init__(self, df, abx_settings):
        self.df = df
        self.abx_settings = abx_settings
        self.abx_options = ['NIT', 'SXT', 'CIP', 'LVX']
        self.abx_settings_copy = {
            key : self.abx_settings[key] for key in self.abx_settings
        } 
        self.n = len(df)

    def set_config(self, config_alt):
        """
        Alters config based on values in config_alt dict
        """
        for key in config_alt:
            self.abx_settings[key] += config_alt[key]

    def reset_config(self):
        """
        Resets config to original config
        """
        self.abx_settings = {
            key : val for key, val in self.abx_settings_copy.items()
        }

    def compute_was_not_covered(self, x, decision_column='prescription'):
        """
        Given administered antibiotic, return whether antibiotic covered pateint
        """
        if decision_column == 'prescription':
            med_description = x.prescription
        elif decision_column == 'ip_prescription':
            med_description = x.ip_prescription 
        elif decision_column == 'random_prescription':
            med_description = x.random_prescription
        else:
            raise
        return x[med_description]

    def get_coverage_rates(self, df=None):
        """
        Create flag for whether clinicians covered the patient during the csn, whether
        a random assignemnt covered patient CSN, and whether optimized assignment covered
        the patient CSN
        """
        if df is None:
            df = self.df

        df = (df
            .assign(was_covered_dr=df.apply(
                lambda x: self.compute_was_not_covered(x), axis=1))
            .assign(was_covered_ip=df.apply(
                lambda x: self.compute_was_not_covered(x, 'ip_prescription'),
                axis=1
                )
            )
            .assign(was_covered_random=df.apply(
                lambda x: self.compute_was_not_covered(x, 'random_prescription'),
                axis=1
                )
            )
        )

        clin_miss_rate = df['was_covered_dr'].sum() / len(df)
        ip_miss_rate = df['was_covered_ip'].sum() / len(df)
        random_miss_rate = df['was_covered_random'].sum() / len(df)
        
        return clin_miss_rate, ip_miss_rate, random_miss_rate

    def random_assignment(self):
        """
        Gets a random assignment of meds given current config
        """
        meds = []
        for key in self.abx_settings:
            meds += [key for i in range(self.abx_settings[key])]
        np.random.shuffle(meds)

        self.df['random_prescription'] = [m for m in meds]

    def solve_and_assign(self):

        # Predictions string
        predictions_string = '%s_predictions'
        abx_model = LpProblem("Antibiotics", LpMinimize)

        # Create binary indicators for whether treatment is used
        drug_inds = {}
        for abx in self.abx_options:
            drug_inds[abx] = [
                LpVariable('%s_%d' % (abx, i), lowBound=0, upBound=1, cat='Binary')
                for i in range(len(self.df))
            ]

        # Add objective function to model
        per_csn_sum = []
        for i in range(len(self.df)):
            _sum = 0
            for abx in self.abx_options:
                _sum += drug_inds[abx][i] * self.df[predictions_string % abx].values[i]
            per_csn_sum.append(_sum)
            
        abx_model += lpSum(per_csn_sum)

        # Add one selection constraint
        for i in range(len(self.df)):
            selections = []
            for abx in self.abx_options:
                selections.append(drug_inds[abx][i])
            abx_model += lpSum(selections) == 1

        for drug in drug_inds:
            abx_model += lpSum(
                [drug_inds[drug][i] for i in range(len(self.df))]
            ) == self.abx_settings[drug]

        # Solve model
        abx_model.solve(solver=PULP_CBC_CMD(msg=False, timeLimit=10))

        # Save selected antibiotic to df
        abx_decisions = []
        for i in range(len(self.df)):
            abx_decision = None
            for abx in self.abx_options:
                if drug_inds[abx][i].value() == 1:
                    abx_decision = abx
            assert abx_decision is not None
            abx_decisions.append(abx_decision)
        self.df['ip_prescription'] = abx_decisions

def load_best_model_predictions(base_path):
    """
    Loads best model predictions for input into linear programming opt
    """
    best_auc = 0.5
    label = base_path.split('/')[-1]
    for model in ['ridge', 'lasso', 'gbm', 'random_forest']:
        auc_path = os.path.join(base_path, model, "auroc.txt")
        with open(auc_path, 'r') as f:
            auc = float(f.read().rstrip())
        if auc > best_auc:
            # Load predictions for this model
            path = os.path.join(base_path, model, f"{model}_predictions.csv")
            df_preds = pd.read_csv(path)
            df_preds = df_preds.assign(
                pred_id = [i for i in range(len(df_preds))],
                label = [label for i in range(len(df_preds))]
            )
            best_auc = auc
    print(f"{label} best auc: {best_auc}")
    return df_preds

def perform_sweep_plots():
    """
    Starts antibiotics config at what doctors prescribed and then 
    """
    base_path = '/Users/conorcorbin/data/mit_abx_model_results/'
    df = pd.DataFrame()
    for label in ['NIT', 'SXT', 'CIP', 'LVX']:
        df_preds = load_best_model_predictions(
            os.path.join(base_path, label)
        )
        df = pd.concat([df, df_preds])
    df = (df
        .pivot(index='pred_id', columns='label', values='predictions')
        .reset_index()
        [['NIT', 'SXT', 'CIP', 'LVX']]
        .rename(columns={
            'NIT' : 'NIT_predictions',
            'SXT' : 'SXT_predictions',
            'CIP' : 'CIP_predictions',
            'LVX' : 'LVX_predictions'
        })
    )

    df_prescriptions = pd.read_csv(
        ('/Users/conorcorbin/repos/CDSS/scripts/ER_Infection/'
         'notebooks/mit_data_analysis/data/all_prescriptions.csv')
    )
    df_labels = pd.read_csv(
        ('/Users/conorcorbin/repos/CDSS/scripts/ER_Infection/'
         'notebooks/mit_data_analysis/data/all_uti_resist_labels.csv')
    )

    df_prescriptions = (df_prescriptions
        .merge(df_labels, how='inner', on=['example_id', 'is_train'])
        .query("is_train == 0", engine='python')
        .dropna(subset=['uncomplicated'])
    )
    df = df.assign(
        example_id = lambda x: [id_ for id_ in df_prescriptions.example_id]
    )
    df = (df
        .merge(df_prescriptions, how='inner', on='example_id')
    )

    fig, axs = plt.subplots(2, 3, figsize=(30, 20))
    sweeps = [
        ('CIP', 'LVX'),
        ('CIP', 'NIT'),
        ('CIP', 'SXT'),
        ('LVX', 'NIT'),
        ('LVX', 'SXT'),
        ('NIT', 'SXT')
    ]

    start_config = {
        'CIP' : 1282,
        'LVX' : 41,
        'NIT' : 1358,
        'SXT' : 1260
    }

    row, col = 0, 0
    for i, sweep in enumerate(sweeps):
        axs = sweep_plot(df, sweep, axs, row, col, start_config)
        if col == 2:
            row += 1
            col = 0
        else:
            col += 1
    plt.savefig(
        './abx_sweep.png',
        bbox_inches='tight',
        dpi=300
    )

def sweep_plot(df, sweep, axs, row, col, config):
    """
    Performs one sweep
    """

    opt = AbxDecisionMaker(df, config)
    r_rates, o_rates, c_rates = [], [], []
    num_replaced = []
    for j in tqdm(range(0, config[sweep[0]], 100)):
        opt.reset_config()
        opt.set_config({
            sweep[0] : -j,
            sweep[1] : +j
        })
        print(opt.abx_settings)
        opt.solve_and_assign()
        opt.random_assignment()
        c, i, r = opt.get_coverage_rates()
        r_rates.append(r)
        c_rates.append(c)
        o_rates.append(i)
        num_replaced.append(j)

    axs[row, col].plot(
        num_replaced,
        r_rates,
        label='Random Allocation',
        linewidth=2.0
    )
    axs[row, col].plot(
        num_replaced,
        c_rates,
        label='Clinician Allocation',
        linewidth=2.0
    )
    axs[row, col].plot(
        num_replaced,
        o_rates,
        label='Optimized Allocation',
        linewidth=2.0
    )

    if col == 2:
        axs[row, col].legend(
            bbox_to_anchor=(1.05, 1),
            loc=2, borderaxespad=0.
        )
    # else:
    #     axs[row, col].get_legend().remove()

    axs[row, col].set_title(f"{sweep[0]} to {sweep[1]}")
    axs[row, col].set_xlabel(f"Num {sweep[0]} replaced with {sweep[1]}")
    axs[row, col].set_ylabel(f"Miss Rate")

    return axs

if __name__ == "__main__":
    perform_sweep_plots()