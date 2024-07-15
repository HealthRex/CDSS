import numpy as np
from numpy import random
from matplotlib import pyplot as plt


def t_test(sample1, sample2):
    # this is a t-test assuming equal sample sizes
    assert len(sample1) == len(sample2)
    difference = sample2.mean() - sample1.mean()
    n_1 = len(sample1)
    n_2 = len(sample2)
    mu_measure_var1 = sample1.var(ddof=1) / len(sample1)
    mu_measure_var2 = sample2.var(ddof=1) / len(sample2)
    mu_std_err = np.sqrt(mu_measure_var1 + mu_measure_var2)
    dof = mu_std_err**4 / (
        mu_measure_var1**2 / (n_1 - 1) + mu_measure_var2**2 / (n_2 - 1)
    )
    t_val = difference / mu_std_err
    t_null_dist = np.random.standard_t(dof, 100_000)
    p_val = np.mean(np.abs(t_val) > t_null_dist) / 2
    return f"""\
t-value: {t_val}
degrees of freedom: {dof}
p-value: {p_val}"""


def freqpoly(x1, x2, binwidth, xlim):
    all_data = np.concatenate([x1, x2])
    x_low = min([all_data.min(), xlim[0]])
    x_high = max([all_data.max(), xlim[1]])
    bins = np.arange(x_low, x_high + binwidth, binwidth)
    fig, ax = plt.subplots()
    ax.hist(x1, bins, density=True, range=xlim, alpha=0.5)
    ax.hist(x2, bins, density=True, range=xlim, alpha=0.5)
    return fig