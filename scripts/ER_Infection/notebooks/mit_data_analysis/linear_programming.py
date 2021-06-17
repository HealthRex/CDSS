from pulp import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white', font_scale=2.0)
from pulp.apis import PULP_CBC_CMD
import os
from tqdm import tqdm
import pickle

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
    sweep_data = {}
    for i, sweep in enumerate(sweeps):
        sweep_data[i] = {}
        axs, data = sweep_plot(df, sweep, axs, row, col, start_config)
        if col == 2:
            row += 1
            col = 0
        else:
            col += 1
        
        sweep_data[i]['num_replaced'] = data[0]
        sweep_data[i]['r_rates'] = data[1]
        sweep_data[i]['c_rates'] = data[2]
        sweep_data[i]['o_rates'] = data[3]

    plt.savefig(
        './abx_sweep.png',
        bbox_inches='tight',
        dpi=300
    )

    with open("sweep_data.pickle", "wb") as f:
        pickle.dump(sweep_data, f)

def sweep_plot(df, sweep, axs, row, col, config):
    """
    Performs one sweep
    """
    if sweep[0] in ('CIP', 'NIT'):
        step_size = 10
    else:
        step_size = 1
    opt = AbxDecisionMaker(df, config)
    r_rates, o_rates, c_rates = [], [], []
    num_replaced = []
    for j in tqdm(range(0, config[sweep[0]], step_size)):
        opt.reset_config()
        opt.set_config({
            sweep[0] : -j,
            sweep[1] : +j
        })
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

    axs[row, col].set_title(f"{sweep[0]} to {sweep[1]}")
    axs[row, col].set_xlabel(f"Num {sweep[0]} replaced with {sweep[1]}")
    axs[row, col].set_ylabel(f"Miss Rate")

    data = (
        num_replaced,
        r_rates,
        c_rates,
        o_rates
    )

    return axs, data

def green(a, b, c):
    """
    array of booleans when a has yet to exceed b or c
    """
    arr = a < b
    was_false = False
    for i in range(len(arr)):
        if arr[i] == False:
            was_false = True
        
        if was_false and arr[i] == True:
            arr[i] == False

    return arr

def yellow(a, b, c):
    """
    array of booleans when a has exceeded b but has yet to exceed c
    """
    arr = np.logical_and(
        a > b,
        a <= c
    )
    ind_first_true, ind_last_true = None, None
    was_true = False
    for i in range(len(arr)):
        if arr[i] == True and was_true == False:
            ind_first_true = i
            was_true = True
        elif arr[i] == True and was_true == True:
            ind_last_true = i

    if ind_first_true is None:
        ind_first_true = len(arr)
    if ind_last_true is None:
        ind_last_true = len(arr)

    for i in range(len(arr)):
        if i > ind_first_true and i < ind_last_true:
            arr[i] = True

    return arr

def red(a, b, c):
    """
    array of booleans when as has exceeded b and c
    """
    arr = a > c
    was_true = False
    for i in range(len(arr)):
        if arr[i] == True:
            was_true = True
        if was_true and arr[i] == False:
            arr[i] == True
    return arr


def plot_data():
    """
    Given saved data from sweeps, makes figures
    """
    # Pre-calculated - we know mean random miss rate is 12.5 percent
    # Clinician miss rate is 11.9 percent

    with open("sweep_data.pickle", "rb") as f:
        data = pickle.load(f)
    
    sweeps = {
        0 : ('CIP', 'LVX'),
        1 : ('CIP', 'NIT'),
        2 : ('CIP', 'SXT'),
        3 : ('LVX', 'NIT'),
        4 : ('LVX', 'SXT'),
        5 : ('NIT', 'SXT')
    }

    fig, axs = plt.subplots(2, 3, figsize=(30, 20))
    row, col = 0, 0
    for key, sweep in data.items():
        sweep['r_rates'] =  np.array(
            [.125 for i in range(len(sweep['r_rates']))]
        )
        sweep['c_rates'] = np.array([
            sweep['c_rates'][0] for i in range(len(sweep['c_rates']))
        ])
        sweep['o_rates'] = np.array(sweep['o_rates'])
        axs[row, col].plot(
            sweep['num_replaced'],
            sweep['r_rates'],
            '--',
            label='Random Allocation',
            linewidth=2.0,
            color='grey',
        )
        axs[row, col].plot(
            sweep['num_replaced'],
            sweep['c_rates'],
            '--',
            label='Clinician Allocation',
            linewidth=2.0,
            color='black',
        )
        axs[row, col].plot(
            sweep['num_replaced'],
            sweep['o_rates'],
            label='Optimized Allocation',
            linewidth=2.0,
            color='black'
        )
        axs[row, col].fill_between(
            sweep['num_replaced'], sweep['o_rates'], sweep['c_rates'],
            where=(green(sweep['o_rates'], sweep['c_rates'], sweep['r_rates'])),
            color='green', alpha=0.3,
            interpolate=True
        )
        axs[row, col].fill_between(
            sweep['num_replaced'], sweep['o_rates'], sweep['r_rates'],
            where=(
                yellow(sweep['o_rates'], sweep['c_rates'], sweep['r_rates'])
            ),
            color='yellow', alpha=0.3,
            interpolate=True
        )
        axs[row, col].fill_between(
            sweep['num_replaced'], sweep['o_rates'], sweep['r_rates'],
            where=(red(sweep['o_rates'], sweep['c_rates'], sweep['r_rates'])),
            color='red', alpha=0.3,
            interpolate=True
        )
        axs[row, col].set_ylim([0.09, 0.14])
        axs[row, col].set_title(
            f"{sweeps[key][0]} to {sweeps[key][1]}"
        )
        axs[row, col].set_xlabel(
            f"# {sweeps[key][0]} Prescriptions Replaced With {sweeps[key][1]}"
        )
        axs[row, col].set_ylabel("Miss Rate")

        if col == 2 and row == 0:
            axs[row, col].legend(
                bbox_to_anchor=(1.05, 1),
                loc=2, borderaxespad=0.
            )

        if col == 2:
            row += 1
            col = 0
        else:
            col += 1

    plt.savefig(
        './abx_sweep_with_shade.png',
        bbox_inches='tight',
        dpi=300
    )


if __name__ == "__main__":
    plot_data()