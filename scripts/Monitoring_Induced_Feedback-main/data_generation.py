import numpy as np
from scipy.stats import uniform, bernoulli, norm

import pdb

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def flip_fraction_of_true(alert_triggered, fraction_to_flip):
    alert_triggered_copy = alert_triggered.copy()  # Create a copy of the input array
    true_indices = np.where(alert_triggered_copy)[0]
    num_to_flip = int(len(true_indices) * fraction_to_flip)
    indices_to_flip = np.random.choice(true_indices, num_to_flip, replace=False)
    alert_triggered_copy[indices_to_flip] = False
    return alert_triggered_copy  # Return the modified copy

def exceed_threshold(model_output, delta, operation='greater'):
    if operation == 'greater':
            return model_output > delta
    else:
        # return when model_output < delta or model_output > 1 - delta
        return np.logical_or(model_output < delta, model_output > 1 - delta)
    
def generate_data_t0(N=10000, alpha=-2, beta=2, omega1=1, omega2=1, omega3=1, gamma=0):
    x1, x2 = uniform(loc=alpha, scale=beta*2).rvs(N), uniform(loc=alpha, scale=beta*2).rvs(N)
    u1 = uniform(loc=alpha, scale=beta*2).rvs(N)
    y = bernoulli(sigmoid(omega1 * x1 + omega2 * x2 + omega3 * u1 + gamma)).rvs(N)
    return x1, x2, y

def generate_data_t1_t2(model, N=10000, delta=0.5, **kwargs):
    def exceed_threshold(model_output, delta, operation='greater'):
        if operation == 'greater':
            return model_output > delta
        else:
            # return when model_output < delta or model_output > 1 - delta
            return np.logical_or(model_output < delta, model_output > 1 - delta)
    
    x1, x2 = uniform(loc=kwargs['alpha'], scale=kwargs['beta']*2).rvs(N), uniform(loc=kwargs['alpha'], scale=kwargs['beta']*2).rvs(N)
    u1 = uniform(loc=kwargs['alpha'], scale=kwargs['beta']*2).rvs(N)
    model_output = model.predict_proba(np.column_stack((x1, x2)))[:, 1]  # Probability of positive class
    alert_triggered = exceed_threshold(model_output, delta, operation=kwargs['operation'])
    alert_triggered_swm = flip_fraction_of_true(alert_triggered, kwargs['withholding_prob'])
    A = bernoulli(sigmoid(kwargs['phi1'] * x1 + kwargs['phi2'] * u1 + kwargs['eta'])).rvs(N)

    if kwargs['scenario'] == 'label_modification':
        lambda_val = np.where((alert_triggered & (A == 1)), norm(kwargs['mu'], kwargs['sigma']).rvs(N), 0)
        y = bernoulli(sigmoid(kwargs['omega1'] * x1 + kwargs['omega2'] * x2 + lambda_val + kwargs['omega3'] * u1 + kwargs['gamma'])).rvs(N)

        # In SWM we modify data generating process as we've modified actual deployment set up
        lambda_val_swm = np.where((alert_triggered_swm & (A == 1)), norm(kwargs['mu'], kwargs['sigma']).rvs(N), 0)
        y_swm = bernoulli(sigmoid(kwargs['omega1'] * x1 + kwargs['omega2'] * x2 + lambda_val_swm + kwargs['omega3'] * u1 + kwargs['gamma'])).rvs(N)
    
    return x1, x2, y, y_swm, A, u1, alert_triggered, alert_triggered_swm


