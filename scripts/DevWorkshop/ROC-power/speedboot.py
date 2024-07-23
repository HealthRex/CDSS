import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from scipy.special import ndtr, ndtri
from joblib import Parallel, delayed
import multiprocessing
from tqdm import tqdm

class speedboot:
    """
    Speed boostrap class.

    Attributes:
      data (numpy array or pandas dataframe): fitted model for treatment outcome.
      stats_fun (function): function that takes data as input and outputs one or multiple statistics in a numpy array.
    """                               
    
    def __init__(self, data, stats_fun):
        """
        Initializer for Fast boostrap class.
        """
        self.data = pd.DataFrame(data).reset_index()
        self.stats_fun = stats_fun

    def fit(self, R=999, bar = True, par = False, seed=0):
        """Bootstrap multiple statistics at once given data.
        
        Attributes:
            R (positive int): fitted model for treatment outcome.
            bar (bool): print progress bar.
            par (bool): parallelization on all cores.
            seed (positive int): random seed for reproducibility.
        """
        
        self.R = R
        random.seed(seed)
        num_cores = multiprocessing.cpu_count()
        resamples = [[random.randint(0,len(self.data)-1) for _ in range(len(self.data))] for _ in range(R)]
        boot_dfs = [self.data.iloc[resamples[i]] for i in range(R)]
        if bar and par:
            boot_estimates = Parallel(n_jobs=num_cores)(delayed(self.stats_fun)(i) for i in tqdm(boot_dfs))
        elif bar and not par:
            boot_estimates = [self.stats_fun(boot_df) for boot_df in tqdm(boot_dfs)]
        elif not bar and par:
            boot_estimates = Parallel(n_jobs=num_cores)(delayed(self.stats_fun)(i) for i in boot_dfs)
        elif not bar and not par:
            boot_estimates = [self.stats_fun(boot_df) for boot_df in boot_dfs]  
        self.ests_boot = np.vstack([ests_i.T for ests_i in boot_estimates])
        self.ests = np.array(self.stats_fun(self.data))
    
    def emp_ci(self, alpha=.05):
        """from an array of estimates and a R x len(slef.ests) matrix of bootstrap estimates
        outputs a len(slef.ests) x 2 matrix of empirical bootstrap CI.
        
        Attributes:
            alpha (probability float): alpha risk that determines confidence interval width i.e., alpha=.05 for 95% confidence intervals.
        """
        quantiles = np.array([np.nanquantile(self.ests_boot[:,est_id],[1-alpha/2, alpha/2]) for est_id, _ in enumerate(self.ests)])
        if len(self.ests) == 1:
            return 2*self.ests-quantiles
        else:
            return np.multiply(2,self.ests).reshape(len(self.ests),1)-quantiles

    def per_ci(self, alpha=.05):
        """from an array of estimates and a R x len(slef.ests) matrix of bootstrap estimates
        outputs a len(slef.ests) x 2 matrix of empirical bootstrap CI.
                
        Attributes:
            alpha (probability float): alpha risk that determines confidence interval width i.e., alpha=.05 for 95% confidence intervals.
        """
        return np.array([np.nanquantile(self.ests_boot[:,est_id],[alpha/2, 1-alpha/2]) for est_id, _ in enumerate(self.ests)])
    
    def plot(self, prec=.05, size=4):
        """plots histograms of the bootstrap estimates
        
        Attributes:
            prec (probability float): determines the binwidth of the histograms. If prec=1 plots as many bins as boostrap estimates.
            size (positive float): size of each plot.
        """
        plt.figure(figsize=(size, size*len(self.ests)))
        n_bins = int(prec * len(self.ests_boot))
        for n in range(len(self.ests)): # adds a new subplot iteratively
            ax = plt.subplot(len(self.ests), 1, n + 1)
            ax.hist(self.ests_boot[:,n], bins=np.linspace(min(self.ests_boot[:,n]), max(self.ests_boot[:,n]), num=n_bins))
            plt.xlim(min(self.ests_boot[:,n]), max(self.ests_boot[:,n]))
            ax.set_title("Estimate " + str(n+1))
            
    def jackknife(self, bar = True, par = False):
        """Compute jackknife estimates for multiple statistics at once given data.
        
        Attributes:
            bar (bool): print progress bar.
            par (bool): parallelization on all cores.
        """
            
        num_cores = multiprocessing.cpu_count()

        jack_dfs = [self.data.drop(i) for i in range(len(self.data))]
        if bar and par:
            jack_estimates = Parallel(n_jobs=num_cores)(delayed(self.stats_fun)(i) for i in tqdm(jack_dfs)) 
        elif bar and not par:
            jack_estimates = [self.stats_fun(jack_df) for jack_df in tqdm(jack_dfs)]  
        elif not bar and par:
            jack_estimates = Parallel(n_jobs=num_cores)(delayed(self.stats_fun)(i) for i in jack_dfs)  
        elif not bar and not par:
            jack_estimates = [self.stats_fun(jack_dfs) for jack_df in jack_dfs]  

        self.ests_jack = np.vstack([ests_i.T for ests_i in jack_estimates]) 
        
    def bca_ci(self, alpha=.05):
        """from an array of estimates and a R x len(slef.ests) matrix of bootstrap estimates and a
        len(self.data) x len(slef.ests) matrix of jackknife estimates this method outputs a 
        len(slef.ests) x 2 matrix of BCa (bias-corrected and accelerated) CI.
                
        Attributes:
            alpha (probability float): alpha risk that determines confidence interval width i.e., alpha=.05 for 95% confidence intervals.
        """
        try:
            self.ests_jack is float
        except AttributeError:
            print("To obtain BCa confidence intervals you need to first run the jackknife ")
            print("i.e., use the .jackknife() method")
        
        # calculate z0_hat
        z0_hat = ndtri(np.sum(self.ests_boot < self.ests, axis=0)/self.R)
        
        # calculate a_hat
        num =     np.sum((np.mean(self.ests_jack, axis=0) - self.ests_jack)**3, axis=0)
        denom = 6*np.sum((np.mean(self.ests_jack, axis=0) - self.ests_jack)**2, axis=0)**(3/2)
        a_hat = num/denom
        
        # calculate alpha_1, alpha_2
        alpha = alpha / 2
        z_alpha = ndtri(alpha)
        z_1alpha = -z_alpha
        num1 = z0_hat + z_alpha
        alpha_1 = ndtr(z0_hat + num1/(1 - a_hat*num1))
        num2 = z0_hat + z_1alpha
        alpha_2 = ndtr(z0_hat + num2/(1 - a_hat*num2))
        
        bca = np.array([np.nanquantile(self.ests_boot[:,est_id],[alpha_1[est_id], alpha_2[est_id]]) for est_id in range(len(self.ests)) ])
        
        return bca