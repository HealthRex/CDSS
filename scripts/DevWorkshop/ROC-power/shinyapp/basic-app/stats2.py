import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, multivariate_normal, bernoulli
from scipy.special import expit, logit

to_01_fun = norm.cdf # expit
to_r_fun = norm.ppf # logit

def plot_contour(fig, ax, X_mean, Y_mean, X_var, Y_var, corr, cases = True, epsi=1e-6, n_points=300): 
    x_ori = np.linspace(epsi, 1-epsi, n_points)
    x = to_r_fun(x_ori)
    X, Y = np.meshgrid(x,x)
    XY = np.array([[(X[i,j], Y[i,j]) for j in range(n_points)] for i in range(n_points)])

    mean_0 = to_r_fun(X_mean); mean_1 = to_r_fun(Y_mean)
    mean = [mean_0, mean_1]
    var_0 = -np.log(1-X_var); var_1 = -np.log(1-Y_var)
    diag = corr * np.sqrt(var_0 * var_1 )

    covariance = [[var_0, diag], [diag, var_1]]
    bivariate_normal = multivariate_normal(mean=mean, cov=covariance)
    Z = bivariate_normal.pdf(XY)

    num_samples = 1000
    samples_ori = bivariate_normal.rvs(size=num_samples)
    samples = to_01_fun(samples_ori)
    E_X, E_Y = samples.mean(axis=0)

    X_ori, Y_ori = np.meshgrid(x_ori, x_ori)

    contour = ax.contourf(X_ori, Y_ori, Z, levels=200, cmap='RdBu_r')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    #if not cases:
    cbar = fig.colorbar(contour, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Density', rotation=270, labelpad=15)

    ax.plot(E_X, E_Y, marker='X', color='black', markersize=12)
    ax.plot([0, 1], [0, 1], '-', color='black', linewidth=1)
    ax.plot([E_X, E_X], [0, E_Y], '--', color='black', linewidth=0.75)
    ax.plot([0, E_X], [E_Y, E_Y], '--', color='black', linewidth=0.75)

    if cases:
        ax.set_title('Cases $(Y=1)$\n' + fr'The average Predicted Probability is {E_X:.2f} for Model A, and {E_Y:.2f} for Model B')
    else:
        ax.set_title('Controls $(Y=0)$\n' + fr'The average Predicted Probability is {E_X:.2f} for Model A, and {E_Y:.2f} for Model B')
    ax.set_xlabel('Predictions from Model A')#(r'$\tilde{Y}_A$')
    ax.set_ylabel('Predictions from Model B')#(r'$\tilde{Y}_B$', rotation=0)

    return samples

def int_plot(X_mean_cases, Y_mean_cases, X_var_cases, Y_var_cases, corr_cases, X_mean_controls, Y_mean_controls, X_var_controls, Y_var_controls, corr_controls):
    fig = plt.figure(figsize=(20, 20))
    ax1 = plt.subplot2grid((3, 2), (0, 0))
    samples_cases = plot_contour(fig, ax1, X_mean=X_mean_cases, Y_mean=Y_mean_cases, X_var=X_var_cases, Y_var=Y_var_cases, corr=corr_cases, cases=True)

    ax2 = plt.subplot2grid((3, 2), (0, 1))
    samples_controls = plot_contour(fig, ax2, X_mean=X_mean_controls, Y_mean=Y_mean_controls, X_var=X_var_controls, Y_var=Y_var_controls, corr=corr_controls, cases=False)