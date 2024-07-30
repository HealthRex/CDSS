import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory
from scipy.stats import norm, multivariate_normal, bernoulli
from scipy.special import expit, logit
from sklearn.metrics import roc_curve, auc
import compare_auc_delong_xu
import random

# Monte Carlo simlations from the DeLong

def delong_p_value(y, y_hat_1, y_hat_2):
    return 10 ** compare_auc_delong_xu.delong_roc_test(y, y_hat_1, y_hat_2)[[0]].item()

def data_to_pvals(data, n_sim, sample_sizes):

    # Prepare to store the all the p-values
    sim_res = []

    # Loop over the number of simulations
    for _ in range(n_sim):
        # Sample with replacement ss indices of the test set (where ss is one of the sample sizes)
        ids_list = [random.choices(range(len(data)), k=ss) for ss in sample_sizes]
        # Compute a p-value for each sample size
        sim_res.append([delong_p_value(data[ids,0],  data[ids,1], data[ids,2]) for ids in ids_list])

    # Convert the list to a numpy array
    sim_res = np.array(sim_res)

    return sim_res

def roc_measures(Y, Y_hat):
    fpr, tpr, thresholds = roc_curve(Y, Y_hat)
    roc_auc = auc(fpr, tpr)
    return fpr, tpr, thresholds, roc_auc

def three_panel_pilot(data,
                ss, alpha_t = 0.05, n_sim = None, change_prev = False, prev = None):
    
    if change_prev:
        df_0 = data[data.iloc[:,0]==0]
        fin_df_0 = pd.DataFrame(np.tile(df_0.values, (1000 // len(df_0) + 1, 1))).iloc[:1000]
        
        df_1 = data[data.iloc[:,0]==1]
        fin_df_1 = pd.DataFrame(np.tile(df_1.values, (int(1000*prev/(1-prev)) // len(df_1) + 1, 1))).iloc[:int(1000*prev/(1-prev))]
        
        data = pd.concat([fin_df_0, fin_df_1], axis=0)
        
    data = np.array(data)
        
    _, _, _, auc_A = roc_measures(data[:,0], data[:,1])
    _, _, _, auc_B = roc_measures(data[:,0], data[:,2])
    
    sample_sizes = np.array([int(.5*ss), int(ss), int(1.5*ss)])
    sim_res = data_to_pvals(data, n_sim, sample_sizes)

    mean_pvals = np.log(sim_res).mean(axis=0)
    powers = (sim_res < alpha_t).mean(axis=0)

    # Let's prepare the data for the plot
    x = np.concatenate([np.repeat(sample_size, n_sim) for sample_size in sample_sizes])

    # Add some jitter to the x values
    l = sample_sizes[1] - sample_sizes[0]
    jit = np.random.uniform(-l*.1, l*.1, len(x))
    x = x + jit

    # We'll show the p-values on a log scale
    y = np.log(sim_res.flatten(order='F'))

    plt.scatter(x, y, alpha=0.025)

    # add mean pvals as dots
    plt.scatter(sample_sizes, mean_pvals, s=50, label='Mean log(P-value)')

    # add a regression line between sample_sizes and mean_pval (log scale)
    m, b = np.polyfit(sample_sizes, mean_pvals, 1)
    plt.plot(sample_sizes, m*sample_sizes + b, color='red', label='Line fitted on mean log(P-value)')

    # Add a title
    if change_prev:
        plt.title(f'Assuming the distribution from the provided pilot test set with a prevalence of {100*prev:.1f}%,\n the true AUROCs are {auc_A:.2f} for Model A and {auc_B:.2f} for Model B,\nbased on {n_sim} simulations, the estimated power to detect a difference in AUROC is:', fontsize=14, y=1.15)
    else:
         plt.title(f'Assuming the distribution from the provided pilot test set,\n the true AUROCs are {auc_A:.2f} for Model A and {auc_B:.2f} for Model B,\nbased on {n_sim} simulations, the estimated power to detect a difference in AUROC is:', fontsize=14, y=1.15)

    # add power as text
    plt.text(sample_sizes[0], 1.02, f'Power is {powers[0]*100:.1f}%\nAt n={sample_sizes[0]}', ha='center', va='bottom', transform=plt.gca().get_xaxis_transform())
    plt.text(sample_sizes[1], 1.02, f'Power is {powers[1]*100:.1f}%\nAt n={sample_sizes[1]}', ha='center', va='bottom', transform=plt.gca().get_xaxis_transform())
    plt.text(sample_sizes[2], 1.02, f'Power is {powers[2]*100:.1f}%\nAt n={sample_sizes[2]}', ha='center', va='bottom', transform=plt.gca().get_xaxis_transform())

    # add a horizontal line at p-val=alpha_t
    plt.axhline(np.log(alpha_t), color='black', linestyle='--', label=f'{alpha_t:.2f} alpha threshold')

    # add a horizontal line at p-val=1
    plt.axhline(np.log(1), color='black', linestyle='-', lw=2)

    # add a legend at the bottom right
    plt.legend(loc='lower left')

    # set limits for the y axis
    plt.xlim(sample_sizes[0]-l*.5, sample_sizes[-1] + l*.5)

    # add a label to the x-axis
    plt.xlabel('Sample size (n)')

    # add a label to the y-axis
    plt.ylabel('DeLong P-value (log)')