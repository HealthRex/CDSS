import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='white', font_scale=2.0)
import os, sys
from tqdm import tqdm
import pickle

sys.path.insert(1, '../mit_data_analysis/')
from linear_programming import sweep_plot, sweep_plot_coverage_rate

import pdb

def plot_abx_distributions(site=None):
    """
    Makes bar plots of abx prescription distributions for both the Stanford
    and Boston datasets
    """
    if site == "Stanford":
        abbs = {
            "Ceftriaxone" : "Ceftriaxone",
            "Vancomycin_Zosyn" : "Vanc/Pip-Tazo",
            "Zosyn" : "Pip-Tazo",
            "Vancomycin_Ceftriaxone" : "Vanc/Ceftriaxone",
            "Vancomycin_Cefepime" : "Vanc/Cefepime",
            "Cefepime" : "Cefepime",
            "Vancomycin" : "Vanc",
            "Vancomycin_Meropenem" : "Vanc/Meropenem",
            "Meropenem" : "Meropenem",
            "Cefazolin" : "Cefazolin",
            "Ciprofloxacin" : "Ciprofloxacin",
            "Ampicillin" : "Ampicillin"
        }

        stanford_params = {
            "Ceftriaxone" : 404,
            "Vanc/Pip-Tazo" :  149,
            "Pip-Tazo" : 102,
            "Vanc/Ceftriaxone" : 31,
            "Vanc/Cefepime" : 23,
            "Cefepime" : 14,
            "Vanc" : 13,
            "Vanc/Meropenem" : 9,
            "Meropenem" : 9,
            "Cefazolin" : 8,
            "Ciprofloxacin" : 8,
        }

        fig, axs = plt.subplots(1, 1, figsize=(10, 10))
        df_stanford = pd.DataFrame(data={
            'med' : [key for key in stanford_params],
            'value' : [value for key, value in stanford_params.items()]
        })

        axs = sns.barplot(
            x='value',
            y='med',
            ci=None,
            data=df_stanford,
            ax=axs,
            palette='deep',
        )
        axs.set_xlabel("Number of Prescriptions")
        axs.set_title("Clinician Antibiotic Use 2019")
        axs.set_ylabel('')

        os.makedirs("./select_sweep_plots/", exist_ok=True)
        plt.savefig(
            './select_sweep_plots/stanford_abx_distribution.png',
            bbox_inches='tight',
            dpi=300
        )

    elif site == "Boston":
        boston_abx = {
            'Nitrofurantoin' : 1358,
            'Ciprofloxacin' : 1282,
            'Trim/Sulfamethoxazole' : 1260,
            'Levofloxacin' : 41,
       }
        fig, axs = plt.subplots(1, 1, figsize=(10, 10))
        df_boston = pd.DataFrame(data={
            'med' : [key for key in boston_abx],
            'value' : [value for key, value in boston_abx.items()]
        })
        axs = sns.barplot(
            x='value',
            y='med',
            ci=None,
            data=df_boston,
            ax=axs,
            palette='deep',
        )
        axs.set_xlabel("Number of Prescriptions")
        axs.set_title("Clinician Antibiotic Use 2014-2016")
        axs.set_ylabel('')

        os.makedirs("./select_sweep_plots/", exist_ok=True)
        plt.savefig(
            './select_sweep_plots/boston_abx_distributions.png',
            bbox_inches='tight',
            dpi=300
        )


    else:

        boston_abx = {
            'NIT' : 1358,
            'CIP' : 1282,
            'SXT' : 1260,
            'LVX' : 41
        }

        abbs = {
            "Ceftriaxone" : "CTX",
            "Vancomycin_Zosyn" : "VAN/TZP",
            "Zosyn" : "TZP",
            "Vancomycin_Ceftriaxone" : "VAN/CTX",
            "Vancomycin_Cefepime" : "VAN/CFP",
            "Cefepime" : "CFP",
            "Vancomycin" : "VAN",
            "Vancomycin_Meropenem" : "VAN/MEM",
            "Meropenem" : "MEM",
            "Cefazolin" : "CFZ",
            "Ciprofloxacin" : "CIP",
            "Ampicillin" : "AMP"
        }

        stanford_abx = {
            "CTX" : 404,
            "VAN/TZP" :  149,
            "TZP" : 102,
            "VAN/CTX" : 31,
            "VAN/CFP" : 23,
            "CFP" : 14,
            "VAN" : 13,
            "VAN/MEM" : 9,
            "MEM" : 9,
            "CFZ" : 8,
            "CIP" : 8,
        }
        fig, axs = plt.subplots(1, 2, figsize=(20, 10))
        df_stanford = pd.DataFrame(data={
            'med' : [key for key in stanford_abx],
            'value' : [value for key, value in stanford_abx.items()]
        })
        df_boston = pd.DataFrame(data={
            'med' : [key for key in boston_abx],
            'value' : [value for key, value in boston_abx.items()]
        })
        axs[0] = sns.barplot(
            x='value',
            y='med',
            ci=None,
            data=df_stanford,
            ax=axs[0],
            palette='deep',
        )
        axs[1] = sns.barplot(
            x='value',
            y='med',
            ci=None,
            data=df_boston,
            ax=axs[1],
            palette='deep',
        )
        axs[0].set_xlabel("Number of Prescriptions")
        axs[0].set_title("[Stanford] Distribution of Abx Prescriptions")
        axs[0].set_ylabel('')

        axs[1].set_xlabel("Number of Prescriptions")
        axs[1].set_title("[Boston] Distribution of Abx Prescriptions")
        axs[1].set_ylabel('')

        os.makedirs("./select_sweep_plots/", exist_ok=True)
        plt.savefig(
            './select_sweep_plots/abx_distributions.png',
            bbox_inches='tight',
            dpi=300
        )

def plot_select_sweeps_boston():
    """
    Plot select sweeps from boston data
    """

    with open("sweep_data_boston.pickle", "rb") as f:
        boston_data = pickle.load(f)

    boston_sweeps = {
        1 : ('CIP', 'NIT'),
        2 : ('CIP', 'SXT'),
        5 : ('NIT', 'SXT')
    }

    abbs = {
        'CIP' : 'Ciprofloxacin',
        'LVX' : 'Levofloxacin',
        'NIT' : 'Nitrofurantoin',
        'SXT' : 'Trimethoprim/Sulfamethoxazole'
    }

    boston_params = {
        'Ciprofloxacin' : 1282,
        'Levofloxacin' : 41,
        'Nitrofurantoin' : 1358,
        'Trimethoprim/Sulfamethoxazole' : 1260,
        'ymin' : 0.84,
        'ymax' : 0.92,
        'random_rate' : 0.125,
        'site' : "[Boston]"
    }
    fig, axs = plt.subplots(1, 3, figsize=(30, 10))
    col = 0
    for key, sweep in boston_data.items():
        if key not in [key for key in boston_sweeps]:
            continue
        axs[col] = sweep_plot_coverage_rate(
            axs[col],
            (abbs[boston_sweeps[key][0]], abbs[boston_sweeps[key][1]]),
            num_replaced=sweep['num_replaced'],
            o_rates=sweep['o_rates'],
            c_rates=sweep['c_rates'],
            r_rates=sweep['r_rates'],
            params=boston_params
        )

        if col == 0:
            axs[col].set_ylabel("Coverage Rate")

        if col == 1:
            axs[col].legend(
                loc="lower center", bbox_to_anchor=(0.5, -0.46),
                borderaxespad=0.
            )
        col += 1      

    os.makedirs("./select_sweep_plots/", exist_ok=True)
    plt.savefig(
        './select_sweep_plots/sweep_plot_boston_select_coverage_rate.png',
        bbox_inches='tight',
        dpi=300
    )


def plot_select_sweeps_stanford():
    """
    Plot select sweeps from stanford data
    """
    with open('sweep_data.pickle', 'rb') as f:
        stanford_data = pickle.load(f)

    abbs = {
        "Ceftriaxone" : "Ceftriaxone",
        "Vancomycin_Zosyn" : "Vanc/Pip-Tazo",
        "Zosyn" : "Pip-Tazo",
        "Vancomycin_Ceftriaxone" : "Vanc/Ceftriaxone",
        "Vancomycin_Cefepime" : "Vanc/Cefepime",
        "Cefepime" : "Cefepime",
        "Vancomycin" : "Vanc",
        "Vancomycin_Meropenem" : "Vanc/Meropenem",
        "Meropenem" : "Meropenem",
        "Cefazolin" : "Cefazolin",
        "Ciprofloxacin" : "Ciprofloxacin",
        "Ampicillin" : "Ampicillin"
    }

    stanford_params = {
        "Ceftriaxone" : 404,
        "Vanc/Pip-Tazo" :  149,
        "Pip-Tazo" : 102,
        "Vanc/Ceftriaxone" : 31,
        "Vanc/Cefepime" : 23,
        "Cefepime" : 14,
        "Vanc" : 13,
        "Vanc/Meropenem" : 9,
        "Meropenem" : 9,
        "Cefazolin" : 8,
        "Ciprofloxacin" : 8,
        "Ampicillin" : 0,
        "random_rate" : .208,   
        "ymin" : 0.77,
        "ymax" : 0.88,
        "site" : "[Stanford]"
    }
    stanford_sweeps = [
        ('Vancomycin_Zosyn', 'Zosyn'),
        ('Vancomycin_Zosyn', 'Cefepime'),
        ('Vancomycin_Zosyn', 'Ceftriaxone'),
        ('Vancomycin_Zosyn', 'Ampicillin'),
        ('Zosyn', 'Ceftriaxone'),
        ('Zosyn', 'Cefazolin'),
        ('Zosyn', 'Ampicillin'),
        ('Ceftriaxone', 'Cefazolin'),
        ('Ceftriaxone', 'Ampicillin')
    ]

    fig, axs = plt.subplots(3, 3, figsize=(30, 30))
    row, col = 0, 0
    for sweep in stanford_sweeps:
        num_replaced = [
                k for k in range(len(stanford_data[sweep]['r_rates']))
            ]
        r_rates = stanford_data[sweep]['r_rates']
        c_rates = stanford_data[sweep]['c_rates']
        o_rates = stanford_data[sweep]['o_rates']
        axs[row, col] = sweep_plot_coverage_rate(
            axs[row, col],
            (abbs[sweep[0]], abbs[sweep[1]]),
            num_replaced=num_replaced,
            o_rates=o_rates,
            c_rates=c_rates,
            r_rates=r_rates,
            params=stanford_params
        )

        if col == 0:
            axs[row, col].set_ylabel("Coverage Rate")

        if col == 1 and row == 2:
            axs[row, col].legend(
                loc="lower center", bbox_to_anchor=(0.5, -0.55),
                borderaxespad=0.
            )

        if col == 2:
            row += 1
            col = 0
        else:
            col += 1

    os.makedirs("./select_sweep_plots/", exist_ok=True)
    plt.savefig(
        './select_sweep_plots/sweep_plot_stanford_select.png',
        bbox_inches='tight',
        dpi=300
    )
  
def plot_select_sweeps():
    """
    Plot select sweeps from both stanford and boston. This creates main text
    figure. 
    """
    with open("sweep_data_boston.pickle", "rb") as f:
        boston_data = pickle.load(f)

    with open('sweep_data.pickle', 'rb') as f:
        stanford_data = pickle.load(f)

    boston_sweeps = {
        1 : ('CIP', 'NIT'),
        2 : ('CIP', 'SXT'),
        5 : ('NIT', 'SXT')
    }

    boston_params = {
        'CIP' : 1282,
        'LVX' : 41,
        'NIT' : 1358,
        'SXT' : 1260,
        'ymin' : 0.09,
        'ymax' : 0.14,
        'random_rate' : .125,
        'site' : "[Boston]"
    }

    abbs = {
        "Ceftriaxone" : "CTX",
        "Vancomycin_Zosyn" : "VAN/TZP",
        "Zosyn" : "TZP",
        "Vancomycin_Ceftriaxone" : "VAN/CTX",
        "Vancomycin_Cefepime" : "VAN/CFP",
        "Cefepime" : "CFP",
        "Vancomycin" : "VAN",
        "Vancomycin_Meropenem" : "VAN/MEM",
        "Meropenem" : "MEM",
        "Cefazolin" : "CFZ",
        "Ciprofloxacin" : "CIP",
        "Ampicillin" : "AMP"
    }

    stanford_params = {
        "CTX" : 404,
        "VAN/TZP" :  149,
        "TZP" : 102,
        "VAN/CTX" : 31,
        "VAN/CFP" : 23,
        "CFP" : 14,
        "VAN" : 13,
        "VAN/MEM" : 9,
        "MEM" : 9,
        "CFZ" : 8,
        "CIP" : 8,
        "AMP" : 0,
        "random_rate" : .208,   
        "ymin" : 0.12,
        "ymax" : 0.23,
        "site" : "[Stanford]"
    }
    stanford_sweeps = [
        ('Vancomycin_Zosyn', 'Zosyn'),
        ('Vancomycin_Zosyn', 'Cefepime'),
        ('Vancomycin_Zosyn', 'Ceftriaxone'),
        ('Vancomycin_Zosyn', 'Ampicillin'),
        ('Zosyn', 'Ceftriaxone'),
        ('Zosyn', 'Cefazolin'),
        ('Zosyn', 'Ampicillin'),
        ('Ceftriaxone', 'Cefazolin'),
        ('Ceftriaxone', 'Ampicillin')
    ]
        
    fig, axs = plt.subplots(4, 3, figsize=(30, 40))
    row, col = 0, 0
    for sweep in stanford_sweeps:
        num_replaced = [
                k for k in range(len(stanford_data[sweep]['r_rates']))
            ]
        r_rates = stanford_data[sweep]['r_rates']
        c_rates = stanford_data[sweep]['c_rates']
        o_rates = stanford_data[sweep]['o_rates']
        axs[row, col] = sweep_plot(
            axs[row, col],
            (abbs[sweep[0]], abbs[sweep[1]]),
            num_replaced=num_replaced,
            o_rates=o_rates,
            c_rates=c_rates,
            r_rates=r_rates,
            params=stanford_params
        )

        if col == 0:
            axs[row, col].set_ylabel("Coverage Rate")

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

    for key, sweep in boston_data.items():
        if key not in [key for key in boston_sweeps]:
            continue
        axs[row, col] = sweep_plot(
            axs[row, col],
            boston_sweeps[key],
            num_replaced=sweep['num_replaced'],
            o_rates=sweep['o_rates'],
            c_rates=sweep['c_rates'],
            r_rates=sweep['r_rates'],
            params=boston_params
        )

        if col == 2 and row == 0:
            axs[row, col].legend(
                bbox_to_anchor=(1.05, 1),
                loc=2, borderaxespad=0.
            )

        if col == 0:
            axs[row, col].set_ylabel("Coverage Rate")

        col += 1      

    os.makedirs("./select_sweep_plots/", exist_ok=True)
    plt.savefig(
        './select_sweep_plots/sweep_plot.png',
        bbox_inches='tight',
        dpi=300
    )
  

def plot_all_boston():
    """
    Plot all abx sweeps from the boston dataset.  
    """
    with open("sweep_data_boston.pickle", "rb") as f:
        data = pickle.load(f)
    
    sweeps = {
        0 : ('CIP', 'LVX'),
        1 : ('CIP', 'NIT'),
        2 : ('CIP', 'SXT'),
        3 : ('LVX', 'NIT'),
        4 : ('LVX', 'SXT'),
        5 : ('NIT', 'SXT')
    }

    abbs = {
        'CIP' : 'Ciprofloxacin',
        'LVX' : 'Levofloxacin',
        'NIT' : 'Nitrofurantoin',
        'SXT' : 'Trimethoprim/Sulfamethoxazole'
    }

    params = {
        'Ciprofloxacin' : 1282,
        'Levofloxacin' : 41,
        'Nitrofurantoin' : 1358,
        'Trimethoprim/Sulfamethoxazole' : 1260,
        'ymin' : 0.86,
        'ymax' : 0.91,
        'random_rate' : 0.125,
        'site' : "[Boston]"
    }

    fig, axs = plt.subplots(2, 3, figsize=(30, 20))
    row, col = 0, 0
    for key, sweep in data.items():
        axs[row, col] = sweep_plot_coverage_rate(
            axs[row, col],
            (abbs[sweeps[key][0]], abbs[sweeps[key][1]]),
            num_replaced=sweep['num_replaced'],
            o_rates=sweep['o_rates'],
            c_rates=sweep['c_rates'],
            r_rates=sweep['r_rates'],
            params=params
        )

        if col == 2 and row == 0:
            axs[row, col].legend(
                bbox_to_anchor=(1.05, 1),
                loc=2, borderaxespad=0.
            )

        if col == 0:
            axs[row, col].set_ylabel("Coverage Rate")

        if col == 2:
            row += 1
            col = 0
        else:
            col += 1

    os.makedirs("./sweep_plots_boston", exist_ok=True)
    plt.savefig(
        './sweep_plots_boston/boston_coverage_rate.png',
        bbox_inches='tight',
        dpi=300
    )


def plot_all_stanford():
    """
    Plots all abx sweeps from the stanford dataset. There are 65 of them.
    We'll make 5 figures of 16 subplots. 
    """

    abbs = {
        "Ceftriaxone" : "Ceftriaxone",
        "Vancomycin_Zosyn" : "Vanc/Pip-Tazo",
        "Zosyn" : "Pip-Tazo",
        "Vancomycin_Ceftriaxone" : "Vanc/Ceftriaxone",
        "Vancomycin_Cefepime" : "Vanc/Cefepime",
        "Cefepime" : "Cefepime",
        "Vancomycin" : "Vanc",
        "Vancomycin_Meropenem" : "Vanc/Meropenem",
        "Meropenem" : "Meropenem",
        "Cefazolin" : "Cefazolin",
        "Ciprofloxacin" : "Ciprofloxacin",
        "Ampicillin" : "Ampicillin"
    }

    params = {
        "Ceftriaxone" : 404,
        "Vanc/Pip-Tazo" :  149,
        "Pip-Tazo" : 102,
        "Vanc/Ceftriaxone" : 31,
        "Vanc/Cefepime" : 23,
        "Cefepime" : 14,
        "Vanc" : 13,
        "Vanc/Meropenem" : 9,
        "Meropenem" : 9,
        "Cefazolin" : 8,
        "Ciprofloxacin" : 8,
        "Ampicillin" : 0,
        "random_rate" : .208,   
        "ymin" : 0.77,
        "ymax" : 0.88,
        "site" : "[Stanford]"
    }

    with open('sweep_data.pickle', 'rb') as f:
        sweep_data = pickle.load(f)

    sweeps = [key for key in sweep_data]
    os.makedirs('./sweep_plots_stanford/', exist_ok=True)
    for i in tqdm(range(5)):
        fig, axs = plt.subplots(4, 4, figsize=(40, 40))
        row, col = 0, 0
        for j in range(i*16, i*16+16):
            try: 
                test = sweeps[j]
            except: 
                break
            num_replaced = [
                k for k in range(len(sweep_data[sweeps[j]]['r_rates']))
            ]
            r_rates = sweep_data[sweeps[j]]['r_rates']
            c_rates = sweep_data[sweeps[j]]['c_rates']
            o_rates = sweep_data[sweeps[j]]['o_rates']
            axs[row, col] = sweep_plot_coverage_rate(
                axs[row, col],
                (abbs[sweeps[j][0]], abbs[sweeps[j][1]]),
                num_replaced=num_replaced,
                o_rates=o_rates,
                c_rates=c_rates,
                r_rates=r_rates,
                params=params
            )

            if col == 0:
                axs[row, col].set_ylabel("Coverage Rate")

            if col == 3 and row == 0:
                axs[row, col].legend(
                    bbox_to_anchor=(1.05, 1),
                    loc=2, borderaxespad=0.
                )

            if col == 3:
                row += 1
                col = 0
            else:
                col += 1

        plt.savefig(
            f"./sweep_plots_stanford/stanford_coverage_rates{i}",
            bbox_inches='tight',
            dpi=300
        )  


if __name__ == "__main__":
    # plot_select_sweeps_stanford()
    plot_select_sweeps_boston()
