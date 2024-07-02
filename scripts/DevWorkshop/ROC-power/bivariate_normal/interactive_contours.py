import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, multivariate_normal, bernoulli
from scipy.special import expit, logit

to_01_fun = norm.cdf # expit
to_r_fun = logit # norm.ppf

def plot_contour(ax, X_mean, Y_mean, X_var, Y_var, corr, cases = True, epsi=1e-6, n_points=300): 
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

    contour = ax.contourf(X_ori, Y_ori, Z, levels=100, cmap='RdBu_r')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    if not cases:
        cbar = fig.colorbar(contour, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Density', rotation=270, labelpad=15)

    ax.plot(E_X, E_Y, marker='X', color='black', markersize=12)
    ax.plot([0, 1], [0, 1], '-', color='black', linewidth=1)
    ax.plot([E_X, E_X], [0, E_Y], '--', color='black', linewidth=0.75)
    ax.plot([0, E_X], [E_Y, E_Y], '--', color='black', linewidth=0.75)

    if cases:
        ax.set_title('Cases $(Y=1)$\n' + fr'Average Predicted Probability $\tilde{{Y}}_A$: {E_X:.2f}, $\tilde{{Y}}_B$: {E_Y:.2f}')
    else:
        ax.set_title('Controls $(Y=0)$\n' + fr'Average Predicted Probability $\tilde{{Y}}_A$: {E_X:.2f}, $\tilde{{Y}}_B$: {E_Y:.2f}')
    ax.set_xlabel(r'$\tilde{Y}_A$')
    ax.set_ylabel(r'$\tilde{Y}_B$', rotation=0)

    return samples

### TO BE CONTINUED BELOW

### Temp Plot
plt.figure(figsize=(10, 10))
# Create the first subplot on the first row and first column
ax1 = plt.subplot2grid((3, 2), (0, 0))
samples_cases = plot_contour(ax1, X_mean=0.75, Y_mean=0.85, X_var=.2, Y_var=0.3, corr=.6, cases=True)

# Create the second subplot on the first row and second column
ax2 = plt.subplot2grid((3, 2), (0, 1))
samples_controls = plot_contour(ax2, X_mean=0.2, Y_mean=0.3, X_var=0.1, Y_var=0.3, corr=.7, cases=False)

# Create the third subplot on the second row, spanning both columns
#ax3 = plt.subplot2grid((3, 2), (1, 0), colspan=2)
# Example: Plotting a simple line plot on the third subplot
x = np.linspace(0, 10, 100)
y = np.sin(x)
ax3.plot(x, y)
#ax3.set_title('samples = ' + str(val_1 + val_2))
#ax3.set_xlabel('X axis')
#ax3.set_ylabel('Y axis')

# Adjust layout for better spacing
plt.tight_layout()

# Display the plot
plt.show();

#### Get the samples
prev = .3
y = bernoulli.rvs(prev, size=1000).reshape(-1, 1)
data = np.hstack((y, samples_cases * y + samples_controls * (1-y)))
