import numpy as np
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

### Interactive plot that specifies the joint distribution of the predicted probabilities

to_01_fun = norm.cdf # expit
to_r_fun = norm.ppf # logit

def plot_contour(fig, ax, dat_y, cases = True, epsi=1e-6, n_points=300):
    dat_y = np.array(dat_y)
    mean_0, mean_1 = dat_y.mean(axis=0)
    #covariance = np.cov(dat_y, rowvar=False)
     
    x_ori = np.linspace(epsi, 1-epsi, n_points)
    x = to_r_fun(x_ori)
    X, Y = np.meshgrid(x,x)
    XY = np.array([[(X[i,j], Y[i,j]) for j in range(n_points)] for i in range(n_points)])

    #mean_0 = to_r_fun(X_mean); mean_1 = to_r_fun(Y_mean)
    mean = [mean_0, mean_1]
    #var_0 = -np.log(1-X_var); var_1 = -np.log(1-Y_var)
    #diag = corr * np.sqrt(var_0 * var_1 )

    covariance = [[1, 0], [0, 1]]
    bivariate_normal = multivariate_normal(mean=mean, cov=covariance)
    Z = bivariate_normal.pdf(XY)

    num_samples = 100000
    samples_ori = bivariate_normal.rvs(size=num_samples, random_state=1)
    samples = to_01_fun(samples_ori)
    E_X, E_Y = samples.mean(axis=0)

    X_ori, Y_ori = np.meshgrid(x_ori, x_ori)

    contour = ax.contourf(X_ori, Y_ori, Z, levels=200, cmap='RdBu_r')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    cbar = fig.colorbar(contour, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Density', rotation=270, labelpad=15)

    ax.plot(E_X, E_Y, marker='X', color='black', markersize=12)
    ax.plot([0, 1], [0, 1], '-', color='black', linewidth=1)
    ax.plot([E_X, E_X], [0, E_Y], '--', color='black', linewidth=0.75)
    ax.plot([0, E_X], [E_Y, E_Y], '--', color='black', linewidth=0.75)

    if cases:
        ax.set_title(f'For cases:\nThe average predicted probability is\n{E_X:.2f} for Model A, and {E_Y:.2f} for Model B')
    else:
        ax.set_title(f'For controls:\nThe average predicted probability is\n{E_X:.2f} for Model A, and {E_Y:.2f} for Model B')
    ax.set_xlabel('Predictions from Model A')#(r'$\tilde{Y}_A$')
    ax.set_ylabel('Predictions from Model B')#(r'$\tilde{Y}_B$', rotation=0)

    return samples

def three_panel_pilot(data,
                ss, alpha_t = 0.05, n_sim = None):
    
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