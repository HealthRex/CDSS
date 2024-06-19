import numpy as np
from scipy.stats import ttest_rel
import matplotlib.pyplot as plt

def get_pval(ss, prev, p0, p1, p2, p3):
    Y = np.sort(np.random.binomial(1, prev, size=ss))[::-1]
    n = np.sum(Y)
    m = ss - n
    N = n * m
    pvals = [p0, p1, p2, p3]
    N_4_mat = np.random.multinomial(1, pvals, size=N)
    mat_conv_dict = {0: [0,0], 1: [1,0], 2: [0,1], 3: [1,1]}
    N_2_mat = np.array(list(map(lambda x: mat_conv_dict[x], np.argmax(N_4_mat, axis=1))))
    _, p_val = ttest_rel(N_2_mat[:,0], N_2_mat[:,1])
    return p_val

def sim_pvals(n_sim, alpha_t, sample_sizes, prev, p0, p1, p2, p3):
    return np.array([[get_pval(sample_size, prev, p0, p1, p2, p3) for i in range(n_sim)] for sample_size in sample_sizes]).T

def plot_sim(n_sim, alpha_t, ss, prev, p0, p1, p2):
    
    # Calculate p3
    p3 = abs(1-p0-p1-p2)
     
    if p0 + p1 + p2 + p3 > 1:
        plt.figure(figsize=(12, 6))
        plt.text(0.5, 0.5, 'The sum of P0, P1 and P2, (fractions of pairs) must be less than 1.', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes, fontsize=15)
        plt.gca().set_axis_off()
        plt.show()
    
    else :    
        # Get sample sizes
        sample_sizes = np.array([int(.5*ss), int(ss), int(1.5*ss)])
        
        # Run simulations to get the p-values for each sample
        sim_res = sim_pvals(n_sim, alpha_t, sample_sizes, prev, p0, p1, p2, p3)
        
        # Compute the mean p-values and the power
        mean_pvals = sim_res.mean(axis=0)
        
        # Compute power at each sample size
        powers = (sim_res < alpha_t).mean(axis=0)

        # Let's prepare the data for the plot
        x = np.concatenate([np.repeat(sample_size, n_sim) for sample_size in sample_sizes])

        # Add some jitter to the x values
        l = sample_sizes[1] - sample_sizes[0]
        jit = np.random.uniform(-l*.1, l*.1, len(x))
        x = x + jit

        # We'll show the p-values on a log scale
        y = np.log(sim_res.flatten(order='F'))

        plt.figure(figsize=(12,6))
        plt.scatter(x, y, alpha=0.025)

        # add mean pvals as dots
        plt.scatter(sample_sizes, np.log(mean_pvals), s=50, label='Mean(p-value)')

        # add a regression line between sample_sizes and np.log(mean_pvals)
        m, b = np.polyfit(sample_sizes, np.log(mean_pvals), 1)
        plt.plot(sample_sizes, m*sample_sizes + b, color='red', label='Line fitted on mean log(p-value)')

        # Add a title
        AUCs = [p1 + p3, p2 + p3]
        plt.suptitle(f'Power to detect a difference in discrimination: AUROC {AUCs[0]:.2f} vs {AUCs[1]:.2f}', fontsize=14)
        plt.title(f'Results from {n_sim} simulations at three sample sizes', fontsize=12)
        
        # add power as text
        plt.text(sample_sizes[0], -.04*np.min(y), f'At n={sample_sizes[0]}\nPower is {powers[0]*100:.1f}%', ha='center', va='bottom')
        plt.text(sample_sizes[1], -.04*np.min(y), f'At n={sample_sizes[1]}\nPower is {powers[1]*100:.1f}%', ha='center', va='bottom')
        plt.text(sample_sizes[2], -.04*np.min(y), f'At n={sample_sizes[2]}\nPower is {powers[2]*100:.1f}%', ha='center', va='bottom')

        # add a horizontal line at p-val=alpha_t
        plt.axhline(np.log(alpha_t), color='black', linestyle='--', label=f'{alpha_t:.2f} alpha threshold')

        # add a horizontal line at p-val=1
        plt.axhline(np.log(1), color='black', linestyle='-', lw=2)

        # add a legend at the bottom right
        plt.legend(loc='lower left')

        # set limits for the x axis
        plt.xlim(sample_sizes[0]-l*.5, sample_sizes[-1] + l*.5)

        # set limits for the y axis
        plt.ylim(np.min(y), -.15*np.min(y))

        # add a label to the x-axis
        plt.xlabel('Sample size (n)')

        # add a label to the y-axis
        plt.ylabel('log(p-value)')

        # show the plot
        plt.show()

# test the plot    
#prev = .3
#p0 = 0.1; p1 = .2; p2 = .21
#n_sim = 10
#ss = 500
#plot_sim(n_sim, .05, ss, prev, p0, p1, .9)

from ipywidgets import interact, FloatSlider, IntSlider, IntText, FloatText, Layout

interact(plot_sim,
n_sim=IntText(value=100, description='Number of simulations', layout=Layout(width='100%'), style={'description_width': 'initial'}),
alpha_t=FloatText(value=0.05, description='Alpha threshold', layout=Layout(width='100%'), style={'description_width': 'initial'}),
ss=IntText(value=300, description='Sample size', layout=Layout(width='100%')),
prev=FloatSlider(min=0, max=1, step=0.01, value=.1, description='Prevalence', layout=Layout(width='100%'), style={'description_width': 'initial'}),
p0=FloatSlider(min=0, max=1, step=0.01, value=.15, description='Fraction of pairs misclassified by both models (%)', layout=Layout(width='100%'), style={'description_width': 'initial'}),
p1=FloatSlider(min=0, max=1, step=0.01, value=.2, description='Fraction of pairs misclassified by model B but not by model A (%)', layout=Layout(width='100%'), style={'description_width': 'initial'}),
p2=FloatSlider(min=0, max=1, step=0.01, value=.22, description='Fraction of pairs misclassified by model A but not by model B (%)', layout=Layout(width='100%'), style={'description_width': 'initial'})
);