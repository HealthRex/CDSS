import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from tqdm import tqdm
sns.set(style='white', font_scale=1.5)
import numpy as np
from pulp import *
import os, glob
import pdb
from tqdm import tqdm

from integer_programming import get_clinician_prescribing_patterns

def load_predictions():
    """Helper function that loads predictions from AST classifiers for test set data"""
    abx_options = ["Vancomycin",
                   "Ampicillin",
                   "Cefazolin",
                   "Ceftriaxone",
                   "Cefepime",
                   "Zosyn",
                   "Ciprofloxacin",
                   "Meropenem",
                   "Vancomycin_Meropenem",
                   "Vancomycin_Zosyn",
                   "Vancomycin_Cefepime",
                   "Vancomycin_Ceftriaxone"
                   ]
    base_path="/Users/conorcorbin/repos/er_infection/results/ast_models_bucket1/testing/{abx}"
    df = pd.DataFrame()
    for i, abx in enumerate(abx_options):
        path = base_path.format(abx=abx)
        f_path = glob.glob(os.path.join(path, '*predictions.csv'))[0]
        if i == 0:
            df = pd.read_csv(f_path)
            df = df[['anon_id', 'pat_enc_csn_id_coded', 'label', 'predictions']]
            df = df.rename(columns={'label' : '%s_label' % abx,
                                    'predictions' : '%s_predictions' % abx})
        else:
            df_preds = pd.read_csv(f_path)
            df_preds = df_preds[['anon_id', 'pat_enc_csn_id_coded', 'label', 'predictions']]
            df_preds = df_preds.rename(columns={'label' : '%s_label' % abx,
                                                'predictions' : '%s_predictions' % abx})
            df = df.merge(df_preds, how='left', on=['anon_id', 'pat_enc_csn_id_coded'])
    
    return df


class AbxDecisionMaker():

    def __init__(self, df_predictions, df_drugs, abx_settings):
        self.df_predictions = df_predictions
        self.df_drugs = df_drugs
        self.df = (df_predictions
            .merge(df_drugs, how='inner', on='pat_enc_csn_id_coded')
        )
        self.abx_settings = abx_settings
        self.abx_options = ["Vancomycin",
                            "Ampicillin",
                            "Cefazolin",
                            "Ceftriaxone",
                            "Cefepime",
                            "Zosyn",
                            "Ciprofloxacin",
                            "Meropenem",
                            "Vancomycin_Meropenem",
                            "Vancomycin_Zosyn",
                            "Vancomycin_Cefepime",
                            "Vancomycin_Ceftriaxone"
                            ]

        self.abx_map = {'Ceftriaxone' : "CEFTRIAXONE",
                        'Vancomycin_Zosyn' : "PIPERACILLIN-TAZOBACTAM VANCOMYCIN",
                        'Zosyn' : "PIPERACILLIN-TAZOBACTAM",
                        'Vancomycin_Ceftriaxone' : "CEFTRIAXONE VANCOMYCIN",
                        'Vancomycin_Cefepime' : "CEFEPIME VANCOMYCIN",
                        'Cefepime' : "CEFEPIME",
                        'Vancomycin' :  "VANCOMYCIN",
                        'Meropenem' : "MEROPENEM",
                        'Vancomycin_Meropenem' : "MEROPENEM VANCOMYCIN",
                        'Cefazolin' : "CEFAZOLIN",
                        'Ciprofloxacin' : "CIPROFLOXACIN",
                        'Ampicillin' : 'AMPICILLIN'
                        }
        self.abx_map_inverse = {self.abx_map[key] : key for key in self.abx_map}
        self.abx_map_inverse['CEFTRIAXONE PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Zosyn'
        # self.abx_map_inverse['LEVOFLOXACIN PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Zosyn'
        self.abx_map_inverse['AZITHROMYCIN PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Zosyn'
        # self.abx_map_inverse['MEROPENEM PIPERACILLIN-TAZOBACTAM VANCOMYCIN'] = 'Vancomycin_Meropenem'
        self.abx_map_inverse['AZITHROMYCIN CEFTRIAXONE'] = 'Ceftriaxone'

        # Assign random med descriptions here. 
        self.df = (self.df
            .assign(random_med_description=lambda x: np.random.choice(x.med_description,
                                                                      size=len(x.med_description),
                                                                      replace=False))
        )

        self.df_for_reset = self.df.copy()
        self.abx_settings_for_reset = {key : self.abx_settings[key] for key in self.abx_settings} # deep copy
        self.n = len(df_drugs)


    def set_abx_settings(self, abx_settings):
        self.abx_settings = abx_settings

    def reset_df(self):
        self.df = self.df_for_reset.copy()

    def reset_abx_settings(self):
        self.abx_settings = {key : self.abx_settings_for_reset[key] for key in self.abx_settings_for_reset}

    def replace_one(self, to_replace, replace_with):
        """ Randomly takes one allocation of to_replace from the clinician and random
        allocation and replaces with replace_with
        """

        # Replace one clinician allocation
        num_to_replace_before = len(self.df[self.df['med_description'] == to_replace])
        num_replace_with_before = len(self.df[self.df['med_description'] == replace_with])
        inds = [i for i in range(len(self.df)) if self.df['med_description'].values[i] == to_replace]
        ind = np.random.choice(inds)
        self.df = (self.df
            .assign(med_description=lambda x: [a if i != ind else replace_with 
                                              for i, a in enumerate(x.med_description)])
        )
        num_to_replace_after = len(self.df[self.df['med_description'] == to_replace])
        num_replace_with_after = len(self.df[self.df['med_description'] == replace_with])

        assert num_to_replace_before == num_to_replace_after + 1
        assert num_replace_with_before == num_replace_with_after - 1 
        
        # Replace one random allocation
        num_to_replace_before = len(self.df[self.df['random_med_description'] == to_replace])
        num_replace_with_before = len(self.df[self.df['random_med_description'] == replace_with])
        inds = [i for i in range(len(self.df)) if self.df['random_med_description'].values[i] == to_replace]
        ind = np.random.choice(inds)
        self.df = (self.df
            .assign(random_med_description=lambda x: [a if i != ind else replace_with 
                                                      for i, a in enumerate(x.random_med_description)])
        )
        num_to_replace_after = len(self.df[self.df['random_med_description'] == to_replace])
        num_replace_with_after = len(self.df[self.df['random_med_description'] == replace_with])

        assert num_to_replace_before == num_to_replace_after + 1
        assert num_replace_with_before == num_replace_with_after - 1 

    def compute_was_covered(self, x, decision_column='med_description'):
        """
        Given med description, find appropriate label column and return whether patient was covered during CSN
        Returns "Not in abx options" if abx regimen isn't in our set of 12 options - useful for filtering later
        """
        if decision_column == 'med_description':
            med_description = x.med_description
        elif decision_column == 'random_med_description':
            med_description = x.random_med_description
        elif decision_column == 'IP_med_description':
            med_description = x.IP_med_description
        
        return x[med_description]

    def get_coverage_rates(self, df=None):
        """
        Create flag for whether clinicians covered the patient during the csn, whether a random assignemnt
        covered patient CSN, and whether optimized assignment covered the patient CSN
        """
        if df is None:
            df = self.df

        df = (df
            .assign(was_covered_dr=df.apply(lambda x: self.compute_was_covered(x), axis=1))
            .assign(was_covered_random=df.apply(lambda x: self.compute_was_covered(x, 
                                                decision_column='random_med_description'),
                                                axis=1))
            .assign(was_covered_IP=df.apply(lambda x: self.compute_was_covered(x, 
                                            decision_column='IP_med_description'),
                                            axis=1))
        )

        clin_covered_rate = df['was_covered_dr'].sum() / len(df)
        random_covered_rate = df['was_covered_random'].sum() / len(df)
        ip_covered_rate = df['was_covered_IP'].sum() / len(df)
        
        return random_covered_rate, clin_covered_rate, ip_covered_rate

    def solve_and_assign(self):

        # Predictions string
        predictions_string = '%s_predictions'
        abx_model = LpProblem("Antibiotics", LpMaximize)

        # Create binary indicators for whether treatment is used
        drug_inds = {}
        for abx in self.abx_options:
            drug_inds[abx] = [LpVariable('%s_%d' % (abx, i), lowBound=0, upBound=1, cat='Binary')
                            for i in range(len(self.df))]

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
            abx_model += lpSum([drug_inds[drug][i] for i in range(len(self.df))]) == self.abx_settings[drug]

        # Solve model
        abx_model.solve()

        # print("Status:", LpStatus[abx_model.status])
        # Save selected antibiotic to df
        abx_decisions = []
        for i in range(len(self.df)):
            abx_decision = None
            for abx in self.abx_options:
                if drug_inds[abx][i].value() == 1:
                    abx_decision = abx
            assert abx_decision is not None
            abx_decisions.append(abx_decision)
        self.df['IP_med_description'] = abx_decisions

def perform_sweep(opt, abx_1, abx_2, ax, fname, legend=True, append=True):
    """
    Performs one antibiotic sweep where allocations of abx_1 are iterativelly converted to
    allocations of abx_2.  Creates plots of said sweep, and saves a text file indicating
    the point on the sweep where the clinician threshold is met (fraction of abx_1 you can convert
    to abx_2) and maintatin clinician miss rate

    Parameters
    ----------
    opt : AbxDecisionMaker object
    abx_1 : abx to use less of
    abx_2 : abx to use more of
    ax : matplotlib axes to plot on
    """
    if append:
        char_ = 'a'
    else:
        char_ = 'w'
    opt.reset_df()
    opt.reset_abx_settings()
    abx_1_start_setting = opt.abx_settings[abx_1]
    abx_settings_perturbed = {key : opt.abx_settings[key] for key in opt.abx_settings} #deep copy
    reached_clin_error_rate = False
    print("Performing %s to %s sweep" % (abx_1, abx_2))
    random_rates, clin_rates, ip_rates = [], [], []
    c_from_rs, ip_from_rs = [], []

    opt.set_abx_settings(abx_settings_perturbed)
    opt.solve_and_assign()
    r, c, i = opt.get_coverage_rates()
    baseline_clin_miss_rate = 1-c
    random_rates.append(1-r)
    ip_rates.append(1-i)
    clin_rates.append(1-c)

    for iter_ in tqdm(range(abx_1_start_setting)):
        abx_settings_perturbed[abx_1] -= 1
        abx_settings_perturbed[abx_2] += 1
        opt.set_abx_settings(abx_settings_perturbed)
        opt.replace_one(abx_1, abx_2)
        opt.solve_and_assign()
        r, c, i = opt.get_coverage_rates()

        random_rates.append(1-r)
        ip_rates.append(1-i)
        clin_rates.append(1-c)

        if 1-i > baseline_clin_miss_rate and not reached_clin_error_rate:
            # Number of iterations before gettting to baseline clinician error rate
            max_deescalation = iter_
            max_deescaltion_miss_rate = ip_rates[-2]
            settings_to_plot = {key : abx_settings_perturbed[key] for key in abx_settings_perturbed} 
            settings_to_plot[abx_1] += 1
            settings_to_plot[abx_2] -= 1
            d_rate = float(iter_)/abx_1_start_setting
            with open(fname, char_) as w:
                w.write("Miss rate of %.2f achieved with %.2f percent fewer %s\n" % ((max_deescaltion_miss_rate)*100,
                                                                              d_rate*100,
                                                                              abx_1.replace("_", ' & ')))
            miss_rate_to_return = max_deescaltion_miss_rate*100
            reduction_rate = d_rate * 100
            reached_clin_error_rate = True


    if reached_clin_error_rate == False:
        settings_to_plot = {key : abx_settings_perturbed[key] for key in abx_settings_perturbed}
        with open(fname, char_) as w:
                w.write("Miss rate of %.2f achieved with %.2f percent fewer %s\n" % (ip_rates[-1]*100,
                                                                              100,
                                                                              abx_1.replace("_", ' & ')))
        miss_rate_to_return = ip_rates[-1]*100
        reduction_rate = 100
        max_deescalation = abx_1_start_setting
        max_deescaltion_miss_rate = ip_rates[-1]

    deescalations = [i for i in range(len(random_rates))]
    deescalations.reverse()
    ax.plot(deescalations, ip_rates, label='Optimized Allocation', linewidth=2.0)
    ax.plot(deescalations, random_rates, label='Random Allocation', linewidth=2.0)
    ax.plot(deescalations, [baseline_clin_miss_rate for c in range(len(random_rates))],
              linestyle='--', color='black', label='Observed Clinician Allocation')
    if reached_clin_error_rate == False:
        ax.plot(max_deescalation - abx_1_start_setting, max_deescaltion_miss_rate, marker='x',
                markersize=15, color='red', linewidth=2.0)
    else:
        ax.plot(abx_1_start_setting - max_deescalation, max_deescaltion_miss_rate, marker='x',
                markersize=15, color='red', linewidth=2.0)
    ax.invert_xaxis()
    ax.set_title("%s to %s" % (abx_1.replace("_", ' & ').replace('Zosyn', 'Pip/Tazo'),
                 abx_2.replace("_", ' & ').replace('Zosyn', 'Pip/Tazo')))#, y=1.04)
    ax.set_xlabel("# %s Allocated" % abx_1.replace("_", ' & ').replace('Zosyn', 'Pip/Tazo'))
    ax.set_ylabel("Miss Rate")
    ax.set_ylim((0.10, 0.40))

    if legend:
        ax.legend(loc='upper left', fontsize='small')

    return settings_to_plot, miss_rate_to_return, reduction_rate

def plot_histogram(settings, ax, miss_rate=None, reduction_rate=None, abx1=None, abx2=None):
    """
    Given antibiotic settings, plot distribution as bar plot
    """

    if abx1 == None:
        text_offset = 8
        xlim_min = 430
    else:
        text_offset = 17
        xlim_min = 460

    df_settings = pd.DataFrame(data={
        'med' : [key.replace("_", " & ").replace('Zosyn', 'Pip/Tazo') for key in settings],
        'value' : [value for key, value in settings.items()]
    })
    ax = sns.barplot(x="value", y="med", ci=None, data=df_settings, ax=ax, palette="deep")
    max_value = np.max([value for key, value in settings.items()])
    x_max = max(xlim_min, max_value+50)
    ax.set_xlim([0, x_max])
    ax.set_ylabel('')
    ax.set_xlabel('')

    
    for i, p in enumerate(ax.patches):
        ax.text(text_offset+p.get_width(), p.get_y()+0.55*p.get_height(),
                str(p.get_width()),
                ha='center', va='center',
                fontsize='x-small')
        if i == 6 and abx2 not in ('Vancomycin', 'Cefepime'):
            y_center = p.get_y()
        
        if i == 8 and abx2 in ('Vancomycin', 'Cefepime'):
            y_center = p.get_y()


            
    if miss_rate is not None and reduction_rate is not None:
        if '&' in abx1:
            text = "Miss rate {miss_rate}% with\n{red_rate}% fewer {abx}".format(
                miss_rate=str(round(miss_rate, 1)),
                red_rate=str(round(reduction_rate, 1)),
                abx=abx1
            )

        else:
            text = "Miss rate {miss_rate}% with {red_rate}% fewer {abx}".format(
                miss_rate=str(round(miss_rate, 1)),
                red_rate=str(round(reduction_rate, 1)),
                abx=abx1
            )
    else:
        text = "Miss rate {miss_rate}% in observed clinician allocation".format(
                miss_rate=15.7
                )
    ax.text(x_max/2., y_center, text, ha="center", va="center", fontsize='small')




def plot_sweeps(opt):
    """ Perform and plot abx sweeps """
    ordered_abx = ['Vancomycin_Meropenem',
                   'Vancomycin_Cefepime',
                   'Vancomycin_Zosyn',
                   'Zosyn',
                   'Vancomycin_Ceftriaxone',
                   'Meropenem',
                   'Cefepime',
                   'Ceftriaxone',
                   'Ciprofloxacin',
                   'Cefazolin',
                   'Ampicillin',
                   'Vancomycin']
    
    # For each abx, get a set of narrower-spectrum antibiotics
    abx_sets = {}
    for i, abx in enumerate(ordered_abx):
        abx_sets[abx] = [a for j, a in enumerate(ordered_abx) if j > i]
    
    base_path = "./sweep_plots/%s/"
    for j, abx in enumerate(abx_sets):
        path = base_path % abx
        os.makedirs(path, exist_ok=True)
        for i, abx_2 in enumerate(abx_sets[abx]):
            fig, ax = plt.subplots(1, 2, figsize=(16, 8))
            plt.subplots_adjust(wspace=0.3, hspace=0.3)
            fname = os.path.join(path, "%s_to_%s.txt" % (abx, abx_2))
            settings, miss_rate, reduction_rate = perform_sweep(opt,
                                                                abx_1=abx,
                                                                abx_2=abx_2,
                                                                ax=ax[1],
                                                                fname=fname,
                                                                legend=True,
                                                                append=False)
            plot_histogram(settings, ax[0])
            plt.savefig(os.path.join(path, '%s_to_%s_sweeps.png' % (abx, abx_2)),
                        bbox_inches = "tight")

def perform_abx_sweep():
    """
    Simulates antibiotic delivery sweeping through different abx prescribing contraints. 
    For each abx pair, we add the number of times the two were prescribed in total (N) in actual practice
    and then sweep contraints from the extreme where only the first antbiotic prescribed N times to the other
    extreme where the other antibiotic is prescribed N times. We show how coverage rate changes as we change 
    these contraints for both the IP decision and a random decision.
    """
    abx_settings = {"Vancomycin" : 13,
                "Ampicillin" : 0,
                "Cefazolin" : 8,
                "Ceftriaxone" : 404,
                "Cefepime" : 14,
                "Zosyn" : 102,
                "Ciprofloxacin" : 8,
                "Meropenem" : 9,
                "Vancomycin_Meropenem" : 16,
                "Vancomycin_Zosyn" :  153,
                "Vancomycin_Cefepime" : 23,
                "Vancomycin_Ceftriaxone" : 31
                }
    df_predictions = load_predictions()
    df_drugs = get_clinician_prescribing_patterns()
    opt = AbxDecisionMaker(df_predictions, df_drugs, abx_settings)
    opt.solve_and_assign()
    random_covered_rate, clin_covered_rate, ip_covered_rate = opt.get_coverage_rates()

    for abx_to_perturb in abx_settings:
        # plt.figure(figsize=(32,24))
        # fig, ax = plt.subplots(3, 4, figsize=(32, 24))
        # gs = gridspec.GridSpec(4, 24, wspace=2.0)
        # ax1a = plt.subplot(gs[0, 0:6])
        # ax1b = plt.subplot(gs[0, 6:12])
        # ax1c = plt.subplot(gs[0, 12:18])
        # ax1d = plt.subplot(gs[0, 18:24])
        
        # ax2a = plt.subplot(gs[1, 3:9])
        # ax2b = plt.subplot(gs[1, 9:15])
        # ax2c = plt.subplot(gs[1, 15:21])

        # ax3a = plt.subplot(gs[2, 0:6])
        # ax3b = plt.subplot(gs[2, 6:12])
        # ax3c = plt.subplot(gs[2, 12:18])
        # ax3d = plt.subplot(gs[2, 18:24])

        plt.figure(figsize=(24,32))
        gs = gridspec.GridSpec(4, 6, wspace=0.5)
        ax1a = plt.subplot(gs[0, 0:2])
        ax1b = plt.subplot(gs[0, 2:4])
        ax1c = plt.subplot(gs[0, 4:6])

        ax2a = plt.subplot(gs[1, 0:2])
        ax2b = plt.subplot(gs[1, 2:4])
        ax2c = plt.subplot(gs[1, 4:6])

        ax3a = plt.subplot(gs[2, 0:2])
        ax3b = plt.subplot(gs[2, 2:4])
        ax3c = plt.subplot(gs[2, 4:6])

        ax4a = plt.subplot(gs[3, 1:3])
        ax4b = plt.subplot(gs[3, 3:5])


        axes = [ax1a, ax1b, ax1c, ax2a, ax2b, ax2c, ax3a, ax3b, ax3c, ax4a, ax4b]

        skip = 0
        for ind, abx in enumerate(abx_settings):
            if abx == abx_to_perturb:
                skip = 1
                continue
            else:
                abx_settings_perturbed = {key : abx_settings[key] for key in abx_settings}
                print("Performing %s to %s sweep" % (abx_to_perturb, abx))
                random_rates, ip_rates = [], []
                # Total selections to sweep over
                total_selections = abx_settings[abx] + abx_settings[abx_to_perturb]
                abx_settings_perturbed[abx_to_perturb] = total_selections
                abx_settings_perturbed[abx] = 0
                opt.set_abx_settings(abx_settings_perturbed)
                opt.solve_and_assign()
                r, c, i = opt.get_coverage_rates()
                random_rates.append(r)
                ip_rates.append(i)
                if abx_settings_perturbed == abx_settings:
                    clin_iter = -1 # save point on x axis for clinician performance
                for iter_ in tqdm(range(total_selections)):
                    abx_settings_perturbed[abx_to_perturb] -= 1
                    abx_settings_perturbed[abx] += 1
                    opt.set_abx_settings(abx_settings_perturbed)
                    opt.solve_and_assign()
                    r, c, i = opt.get_coverage_rates()
                    random_rates.append(r)
                    ip_rates.append(i)

                    if abx_settings_perturbed == abx_settings:
                        clin_iter = iter_ # save point on x axis for clinician performance
                    
            axes[ind-skip].plot(range(total_selections+1), random_rates, label='Random Assignment')
            axes[ind-skip].plot(range(total_selections+1), ip_rates, label='Integer Programming')
            axes[ind-skip].plot(clin_iter+1, clin_covered_rate, marker='o', label='Clinician Benchmark')
            # forward = lambda x: total_selections - x
            # backward = lambda x: total_selections - x
            # secax = axes[ind-skip].secondary_xaxis('top', functions=(forward, backward))
            axes[ind-skip].set_xlabel("Num %s Administered" % abx)
            # secaxes[ind-skip].set_xlabel("Num %s Administered" % abx_to_perturb)
            axes[ind-skip].set_ylabel("Coverage Rate")
            axes[ind-skip].set_ylim((0.5, 1.))
            axes[ind-skip].set_title("%s to %s Sweep" % (abx_to_perturb, abx))
            axes[ind-skip].legend()
        
        dir_='./tall_grid/'
        os.makedirs(dir_, exist_ok=True)
        fig_name = "./tall_grid/%s_sweeps.jpg" % abx_to_perturb
        plt.savefig(fig_name)


def full_waterfall():
    abx_settings = {"Vancomycin" : 0,
                    "Ampicillin" : 0,
                    "Cefazolin" : 0,
                    "Ceftriaxone" : 0,
                    "Cefepime" : 0,
                    "Zosyn" : 0,
                    "Ciprofloxacin" : 0,
                    "Meropenem" : 0,
                    "Vancomycin_Meropenem" : 697,
                    "Vancomycin_Zosyn" :  0,
                    "Vancomycin_Cefepime" : 0,
                    "Vancomycin_Ceftriaxone" : 0
                    }
    abx_rankings = ['Vancomycin_Meropenem',
                    'Vancomycin_Cefepime',
                    'Vancomycin_Zosyn',
                    'Zosyn',
                    'Vancomycin_Ceftriaxone',
                    'Meropenem',
                    'Cefepime',
                    'Ceftriaxone',
                    'Ciprofloxacin',
                    'Cefazolin',
                    'Ampicillin',
                    'Vancomycin'
                    ]
    
    if os.path.exists('df_predictions.csv'):
        df_predictions = pd.read_csv('df_predictions.csv')
    else:
        df_predictions = load_predictions()
        df_predictions.to_csv('df_predictions.csv', index=None)


    if os.path.exists('df_drugs.csv'):
        df_drugs = pd.read_csv('df_drugs.csv')
    else:
        df_drugs = get_clinician_prescribing_patterns()
        df_drugs.to_csv('df_drugs.csv', index=None)

    deplete_idx = 0
    push_from_idx = 0
    push_to_idx = 1
    random_rates = []
    ip_rates = []
    counter = 0
    while abx_settings['Vancomycin'] != 697: # end of sweep
        opt = AbxDecisionMaker(df_predictions, df_drugs, abx_settings)
        opt.solve_and_assign()
        r, c, i = opt.get_coverage_rates()
        random_rates.append(r)
        ip_rates.append(i)

        if counter == 10:
            print(abx_settings)
            counter = 0

        # Make more narrow spectrum
        abx_settings[abx_rankings[push_from_idx]] -= 1
        abx_settings[abx_rankings[push_to_idx]] += 1
        
        if abx_settings[abx_rankings[deplete_idx]] == 0:
            deplete_idx += 1
            print("Moving deplete index from %s to %s" % (abx_rankings[deplete_idx-1], abx_rankings[deplete_idx]))

        if push_to_idx == len(abx_rankings) - 1:
            push_to_idx = deplete_idx + 1
            push_from_idx = deplete_idx
        else:
            push_from_idx += 1
            push_to_idx += 1

        counter += 1
    
    clin_rates = [c for i in range(len(random_rates))]
    df = pd.DataFrame(data={'clin_rates' : clin_rates,
                            'random_rates' : random_rates,
                            'ip_rates' : ip_rates})
    df.to_csv('summary_sweep.csv')
    fix, ax = plt.subplots(1, 1, figsize=(8,8))
    ax.plot(range(len(random_rates)), random_rates, label='Random Assignment')
    ax.plot(range(len(random_rates)), ip_rates, label='Integer Programming')
    ax.plot(range(len(random_rates)), c, label='Clinician Benchmark')

    fig_name = "summary_sweep.jpg"
    plt.savefig(fig_name)

def bootstrap_miss_rates():
    abx_settings = {"Vancomycin" : 13,
                    "Ampicillin" : 0,
                    "Cefazolin" : 8,
                    "Ceftriaxone" : 404,
                    "Cefepime" : 14,
                    "Zosyn" : 102,
                    "Ciprofloxacin" : 8,
                    "Meropenem" : 9,
                    "Vancomycin_Meropenem" : 9,
                    "Vancomycin_Zosyn" :  149,
                    "Vancomycin_Cefepime" : 23,
                    "Vancomycin_Ceftriaxone" : 31
            }

    # Solve once then bootstrap solutions
    df_predictions = load_predictions()
    df_drugs = get_clinician_prescribing_patterns()
    opt = AbxDecisionMaker(df_predictions, df_drugs, abx_settings)
    opt.solve_and_assign()

    rs, cs, ls = [], [], []
    l_c_relatives, l_r_relatives = [], []
    for i in tqdm(range(1000)):
        
        # Don't stratify, only stratify if bootstrapping the solving procedure as well
        df_drugs_b = (opt.df
            .sample(frac=1.0, replace=True)
        )
        # # Stratified bootstrap
        # df_drugs_b = pd.DataFrame()
        # for abx in abx_settings:
        #     df_temp = (opt.df
        #         .query("med_description == @abx", engine='python')
        #         .sample(frac=1.0, replace=True)
        #     )
        #     df_drugs_b = pd.concat([df_drugs_b, df_temp])
        
        # Sanity Check
        # for abx in abx_settings:
        #     num_allocations = len(df_drugs_b[df_drugs_b['med_description'] == abx])
        #     assert num_allocations == abx_settings[abx]

        if i == 0:
            print(opt.n)

        r, c, l = opt.get_coverage_rates(df=df_drugs_b)
        rs.append(1-r)
        cs.append(1-c)
        ls.append(1-l)
        l_r_relative = ((rs[-1] - ls[-1]) / rs[-1]) * 100
        l_r_relatives.append(l_r_relative)
        l_c_relative = ((cs[-1] - ls[-1]) / cs[-1]) * 100
        l_c_relatives.append(l_c_relative)

    # Miss Rates
    r_mean = np.mean(rs) * 100
    r_low = np.percentile(rs, 2.5) * 100
    r_high = np.percentile(rs, 97.5) * 100
    r_miss_rate = "%.2f [%.2f, %.2f]" % (r_mean, r_low, r_high)

    c_mean = np.mean(cs) * 100
    c_low = np.percentile(cs, 2.5) * 100
    c_high = np.percentile(cs, 97.5) * 100
    c_miss_rate = "%.2f [%.2f, %.2f]" % (c_mean, c_low, c_high)

    l_mean = np.mean(ls) * 100
    l_low = np.percentile(ls, 2.5) * 100
    l_high = np.percentile(ls, 97.5) * 100
    l_miss_rate = "%.2f [%.2f, %.2f]" % (l_mean, l_low, l_high)

    # Relative Miss Reductions
    l_c_means = np.mean(l_c_relatives)
    l_c_low = np.percentile(l_c_relatives, 2.5)
    l_c_high = np.percentile(l_c_relatives, 97.5)
    l_c_final = "%.2f [%.2f, %.2f]" % (l_c_means, l_c_low, l_c_high)

    l_r_means = np.mean(l_r_relatives)
    l_r_low = np.percentile(l_r_relatives, 2.5)
    l_r_high = np.percentile(l_r_relatives, 97.5)
    l_r_final = "%.2f [%.2f, %.2f]" % (l_r_means, l_r_low, l_r_high)

    return r_miss_rate, c_miss_rate, l_miss_rate, l_r_final, l_c_final

def for_debugging_plot_select_sweeps(df_drugs, abx_settings):
    """ Resample df_drugs so that there exist the specified number of allocations in settings """
    df = pd.DataFrame()
    for abx in abx_settings:
        df_temp = (df_drugs
            .query("med_description == @abx", engine='python')
            .sample(n=abx_settings[abx])
        )
        df = pd.concat([df, df_temp])
    return df

def plot_select_sweeps():
    """ Plot Vancomycin & Zosyn to Zosyn 
        Plot Zosyn to Cefazolin
    """
    # abx_settings = {"Vancomycin" : 13,
    #             "Ampicillin" : 0,
    #             "Cefazolin" : 8,
    #             "Ceftriaxone" : 20,#404,
    #             "Cefepime" : 14,
    #             "Zosyn" : 20,#102,
    #             "Ciprofloxacin" : 8,
    #             "Meropenem" : 9,
    #             "Vancomycin_Meropenem" : 9,
    #             "Vancomycin_Zosyn" :  20,#149,
    #             "Vancomycin_Cefepime" : 23,
    #             "Vancomycin_Ceftriaxone" : 31
    #             }
    abx_settings = {"Ceftriaxone" : 404,
            "Vancomycin_Zosyn" :  149,
            "Zosyn" : 102,
            "Vancomycin_Ceftriaxone" : 31,
            "Vancomycin_Cefepime" : 23,
            "Cefepime" : 14,
            "Vancomycin" : 13,
            "Vancomycin_Meropenem" : 9,
            "Meropenem" : 9,
            "Cefazolin" : 8,
            "Ciprofloxacin" : 8,
            "Ampicillin" : 0,
            }
    f_name_missrates = 'select_sweep_miss_rates.txt'
    df_predictions = load_predictions()
    df_drugs = get_clinician_prescribing_patterns()
    # df_drugs = for_debugging_plot_select_sweeps(df_drugs, abx_settings)
    opt = AbxDecisionMaker(df_predictions, df_drugs, abx_settings)
    opt.solve_and_assign()
    random_covered_rate, clin_covered_rate, ip_covered_rate = opt.get_coverage_rates()
    baseline_clin_miss_rate = 1-clin_covered_rate
    sweep_one = ("Vancomycin_Zosyn", "Zosyn")
    sweep_two = ("Zosyn", "Cefazolin")
    # sweep_three = ("Zosyn", "Ampicillin")
    sweep_three = ("Ceftriaxone", 'Cefazolin')
    sweep_four = ("Ceftriaxone", 'Ampicillin')
    # fig, ax = plt.subplots(1, 3, figsize=(24,8))

    plt.figure(figsize=(36,30))
    gs = gridspec.GridSpec(5, 6, wspace=0.5, hspace=0.35)
    ax1a = plt.subplot(gs[0, 2:4])

    ax2a = plt.subplot(gs[1, 1:3])
    ax2b = plt.subplot(gs[1, 3:5])

    ax3a = plt.subplot(gs[2, 1:3])
    ax3b = plt.subplot(gs[2, 3:5])

    ax4a = plt.subplot(gs[3, 1:3])
    ax4b = plt.subplot(gs[3, 3:5])

    ax5a = plt.subplot(gs[4, 1:3])
    ax5b = plt.subplot(gs[4, 3:5])

    axes = [[ax1a], [ax2a, ax2b], [ax3a, ax3b], [ax4a, ax4b], [ax5a, ax5b]]

    # Plot original clinician distribution
    plot_histogram(abx_settings, axes[0][0])
    axes[0][0].set_title("Actual Clinician Allocation") # hard coded miss rate
    axes[0][0].set_xlabel("Number of Allcations")
    axes[0][0].set_ylabel('')
    with open (f_name_missrates, 'w') as w:
        w.write("Clinician Miss Rate: %.2f\n" % (baseline_clin_miss_rate * 100))
    # sweep_one = ('Cefepime', 'Cefazolin')
    for k, sweep in enumerate([sweep_one, sweep_two, sweep_three, sweep_four]):
        opt.reset_df()
        abx_settings_perturbed = {key : abx_settings[key] for key in abx_settings} #deep copy
        max_deescalation = None
        print("Performing %s to %s sweep" % (sweep[0], sweep[1]))
        random_rates, clin_rates, ip_rates = [], [], []
        c_from_rs, ip_from_rs = [], []

        opt.set_abx_settings(abx_settings_perturbed)
        opt.solve_and_assign()
        r, c, i = opt.get_coverage_rates()
        if k ==0:
            print( (1-c) * 100)
        random_rates.append(1-r)
        ip_rates.append(1-i)
        clin_rates.append(1-c)

        for iter_ in tqdm(range(abx_settings[sweep[0]])):
            abx_settings_perturbed[sweep[0]] -= 1
            abx_settings_perturbed[sweep[1]] += 1
            opt.set_abx_settings(abx_settings_perturbed)
            opt.replace_one(sweep[0], sweep[1])
            opt.solve_and_assign()
            r, c, i = opt.get_coverage_rates()

            random_rates.append(1-r)
            ip_rates.append(1-i)
            clin_rates.append(1-c)

            if 1-i > baseline_clin_miss_rate and max_deescalation is None:
                # Number of iterations before gettting to baseline clinician error rate
                max_deescalation = abx_settings[sweep[0]] - abx_settings_perturbed[sweep[0]] + 1
                max_deescaltion_miss_rate = ip_rates[len(ip_rates)-2]
                settings_to_plot = {key : abx_settings_perturbed[key] for key in abx_settings_perturbed} 
                settings_to_plot[sweep[0]] += 1
                settings_to_plot[sweep[1]] -= 1
                plot_histogram(settings_to_plot, axes[k+1][0])
                axes[k+1][0].set_title("Optmized Allocation Fewer %s" % sweep[0].replace('_', ' & '))
                axes[k+1][0].set_xlabel('Number of Allocations')
                axes[k+1][0].set_ylabel('')
                print(max_deescalation)
                d_rate = float(abx_settings[sweep[0]] - (abx_settings_perturbed[sweep[0]] + 1))/abx_settings[sweep[0]]
                with open(f_name_missrates, 'a') as w:
                    w.write("Miss rate of %.2f achieve with %.2f fewer %s\n" % ((max_deescaltion_miss_rate)*100,
                                                                                d_rate*100,
                                                                                sweep[0].replace("_", ' & ')))
            # if abx_settings_perturbed == abx_settings:
            #     clin_iter = iter_ # save point on x axis for clinician performance
        if max_deescalation is None:
            max_deescalation = abx_settings[sweep[0]]

        deescalations = [i for i in range(len(random_rates))]
        deescalations.reverse()
        axes[k+1][1].plot(deescalations, ip_rates, label='Optimized', linewidth=2.0)
        axes[k+1][1].plot(deescalations, clin_rates, label='Clinician', linewidth=2.0)
        axes[k+1][1].plot(deescalations, random_rates, label='Random', linewidth=2.0)
        axes[k+1][1].plot(deescalations, [baseline_clin_miss_rate for c in range(len(random_rates))], linestyle='--', color='black')
        axes[k+1][1].invert_xaxis()
        axes[k+1][1].set_title("Replacing %s with %s" % (sweep[0].replace("_", ' & '), sweep[1]))
        axes[k+1][1].set_xlabel("Number of %s Allocated" % sweep[0].replace("_", ' & '))
        axes[k+1][1].set_ylabel("Miss Rate")
        axes[k+1][1].set_ylim((0.10, 0.40))
        print("Max Re-allocations of %s to %s: %s" % (sweep[0], sweep[1], str(max_deescalation)))
        if k == 0:
            axes[k+1][1].legend(loc='upper left', fontsize='small')
        

    plt.savefig('select_sweeps.png')

def test_waterfall():
    abx_settings = {"a" : 2,
                     "b" : 0,
                     "c" : 0
                    }
    abx_rankings = ['a',
                    'b',
                    'c'
                    ]  
    true_settings = [{"a" : 2,
                     "b" : 0,
                     "c" : 0
                    },
                    {"a" : 1,
                     "b" : 1,
                     "c" : 0,
                    },
                    {"a" : 1,
                     "b" : 0,
                     "c" : 1
                    },
                    {"a" : 0,
                     "b" : 1,
                     "c" : 1
                    },
                    {"a" : 0,
                     "b" : 0,
                     "c" : 2
                    }]                 

    settings = []
    deplete_idx = 0
    push_from_idx = 0
    push_to_idx = 1
    import copy
    while abx_settings['c'] != 2: # end of sweep
        settings.append(copy.deepcopy(abx_settings))
        print("Deplete idx:{d} Push From Idx:{f} Push To Idx:{t}".format(d=deplete_idx,
                                                                         f=push_from_idx,
                                                                         t=push_to_idx))
        # Make more narrow spectrum
        abx_settings[abx_rankings[push_from_idx]] -= 1
        abx_settings[abx_rankings[push_to_idx]] += 1

        if abx_settings[abx_rankings[deplete_idx]] == 0:
            deplete_idx += 1

        if push_to_idx == len(abx_rankings)-1:
            push_to_idx = deplete_idx + 1
            push_from_idx = deplete_idx
        else:
            push_from_idx += 1
            push_to_idx += 1

    for i, s in enumerate(settings):
        try:
            assert s == true_settings[i]
        except:
            pdb.set_trace()

def plot_distribution_of_allocated_abx():
    """ Bar plots of allocated abx """
    df = pd.DataFrame()
    abx_settings = {"Vancomycin" : 13,
                "Ampicillin" : 0,
                "Cefazolin" : 8,
                "Ceftriaxone" : 404,
                "Cefepime" : 14,
                "Zosyn" : 102,
                "Ciprofloxacin" : 8,
                "Meropenem" : 9,
                "Vancomycin_Meropenem" : 9,
                "Vancomycin_Zosyn" :  149,
                "Vancomycin_Cefepime" : 23,
                "Vancomycin_Ceftriaxone" : 31
                }

    df_predictions = load_predictions()
    df_drugs = get_clinician_prescribing_patterns()
    opt = AbxDecisionMaker(df_predictions, df_drugs, abx_settings)

    opt.df = (opt.df
        .assign(was_covered_dr=opt.df.apply(lambda x: opt.compute_was_covered(x), axis=1))
    )

    # Get counts
    df_final = (opt.df
        .groupby('med_description')
        .agg(num_distinct_csns=('pat_enc_csn_id_coded', 'nunique'),
             num_times_covered_by_dr=('was_covered_dr', 'sum'))
        .reset_index()
        .assign(med_description=lambda x: [m.replace('_', ' & ') + " [%s/%s]" % (nc, nd) 
                                           for m, nd, nc in zip(x.med_description,
                                                                x.num_distinct_csns,
                                                                x.num_times_covered_by_dr) ])
    )


    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    df_final = df_final.sort_values('num_distinct_csns', ascending=False)
    sns.barplot(x="num_distinct_csns", y="med_description", ci=None, data=df_final, ax=ax, color='red' )
    sns.barplot(x="num_times_covered_by_dr", y="med_description", ci=None, data=df_final, ax=ax, color='blue')
    ax.set_ylabel("")
    ax.set_xlabel("Number of Allocations")
    ax.set_title("Clinician Antibiotic Selections and Fraction of Patients Covered")
    # ax.set_xlim((0, 550))
    # Save Figure
    # plt.gcf().subplots_adjust(left=0.25)
    # plt.savefig('abx_distribution.png')
    plt.show()

    # Save Miss Rates For Each antibiotic
    fname = 'clinicians_miss_rates_by_abx.csv'
    df_miss_rates = (df_final
        .assign(num_misses=lambda x: [csn - n_c for csn, n_c in zip(x.num_distinct_csns,
                                                                    x.num_times_covered_by_dr)])
    )  

    df_miss_rates.to_csv(fname, index=None)


if __name__ == '__main__':
    # r, c, l, lr, lc = bootstrap_miss_rates()
    # fname = './bootstrapped_miss_rates.txt'
    # with open(fname, 'w') as w:
    #     w.write("Random miss rate:%s\n" % r)
    #     w.write("Clinician miss rate:%s\n" % c)
    #     w.write("Optimized miss rate:%s\n" % l)
    #     w.write("Relative Reduction Miss Rate Optimized to Random:%s\n" % lr)
    #     w.write("Relative Reduction Miss Rate Optimized to Clinician:%s\n" % lc)

    # plot_select_sweeps()
    # plot_distribution_of_allocated_abx()
    # bootstrap_miss_rates()

    abx_settings = {"Ceftriaxone" : 404,
        "Vancomycin_Zosyn" :  149,
        "Zosyn" : 102,
        "Vancomycin_Ceftriaxone" : 31,
        "Vancomycin_Cefepime" : 23,
        "Cefepime" : 14,
        "Vancomycin" : 13,
        "Vancomycin_Meropenem" : 9,
        "Meropenem" : 9,
        "Cefazolin" : 8,
        "Ciprofloxacin" : 8,
        "Ampicillin" : 0,
        }

    f_name_missrates = 'individual_sweep_test.txt'
    df_predictions = load_predictions()
    df_drugs = get_clinician_prescribing_patterns()
    opt = AbxDecisionMaker(df_predictions, df_drugs, abx_settings)
    plot_sweeps(opt)
    # perform_sweep(opt, abx_1='Vancomycin_Meropenem', abx_2='Vancomycin', ax=ax, fname=f_name_missrates, legend=True)
    # plt.show()