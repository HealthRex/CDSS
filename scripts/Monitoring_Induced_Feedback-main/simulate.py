import argparse
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_predict
from data_generation import generate_data_t0, generate_data_t1_t2
from monitoring import standard_monitoring, adherence_weighted_monitoring, sampling_weighted_monitoring, \
plot_average_predictions,  plot_results_revamped, plot_timeline, \
plot_retraining_strategy_effect, plot_retraining_early_effect
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import pdb

sns.set_theme(style="white", font_scale=1.5)

# Set up argparse for command line arguments
parser = argparse.ArgumentParser(description='Simulation of Monitoring Strategies')
parser.add_argument('--N', type=int, default=10000, help='Number of samples per time period')
parser.add_argument('--alpha', type=float, default=-2, help='Uniform distribution lower bound')
parser.add_argument('--beta', type=float, default=2, help='Uniform distribution upper bound')
parser.add_argument('--omega1', type=float, default=1, help='Weight for x1')
parser.add_argument('--omega2', type=float, default=1, help='Weight for x2')
parser.add_argument('--omega3', type=float, default=1, help='Weight for confounder')
parser.add_argument('--gamma', type=float, default=0, help='Intercept for label generation')
parser.add_argument('--phi1', type=float, default=1, help='Weight for x2 in adherence model')
parser.add_argument('--phi2', type=float, default=2, help='Weight for u1 in adherence model')
parser.add_argument('--eta', type=float, default=0, help='Intercept in adherence model')
parser.add_argument('--adhere_constant', type=float, default=None, help='constant probability of adherene if not None')
parser.add_argument('--mu', type=float, default=-10, help='Mean for label modification variable')
parser.add_argument('--sigma', type=float, default=0.01, help='Std dev for label modification variable') # refer as psi in paper
parser.add_argument('--pi_s', type=float, default=1, help='Baseline probability for label selection')
parser.add_argument('--lambda_s', type=float, default=-1, help='Adjustment to pi_s due to adherence')
parser.add_argument('--withholding_prob', type=float, default=0.05, help='Probability for withholding intervention in SWM')
parser.add_argument('--delta', type=float, default=0.8, help='Alert triggering threshold')
parser.add_argument('--operation', type=str, default='greater', help='greater or lesser than delta to trigger alert')
parser.add_argument('--r_t', type=float, default=0.001, help='Retraining threshold')
parser.add_argument('--runs', type=int, default=1000, help='Number of simulation runs')
parser.add_argument('--model_class', type=str, default='dt', help='Logistic Regression vs Decision Tree')
parser.add_argument('--random_state', type=int, default=22, help='reproduce results')

args = parser.parse_args()
mon_types = ['standard', 'awm_perfect', 'awm_misspecified', 'swm']
            
def fit_propensity_model(x, u1, A):
    # Combine x and u1 for the perfect model, only x for the misspecified model
    X_perfect = np.column_stack((x, u1))
    X_misspecified = x

    model_perfect = LogisticRegression(penalty=None)
    model_misspecified = LogisticRegression(penalty=None)

    # Cross-fit probability predictions
    prob_perfect = cross_val_predict(model_perfect, X_perfect, A, cv=5, method='predict_proba')[:, 1]
    prob_misspecified = cross_val_predict(model_misspecified, X_misspecified, A, cv=5, method='predict_proba')[:, 1]

    return prob_perfect, prob_misspecified

def visualize_data():
    # Set up figure
    np.random.seed(args.random_state)
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(24, 8))
    fig.subplots_adjust(hspace=0.5)

    # Dataset a (no drift)
    x1_train, x2_train, y_train = generate_data_t0(N=args.N, alpha=args.alpha, 
                                        beta=args.beta, omega1=args.omega1,
                                        omega2=args.omega2,
                                        omega3=args.omega3, gamma=args.gamma)

    # Use this to fit the first model
    model_class = 'dt'

    model_a = None
    if model_class == 'lr':
        model_a = LogisticRegression(penalty=None).fit(np.column_stack((x1_train, x2_train)), y_train)
    else:
        model_a = DecisionTreeClassifier(max_depth=10, min_samples_split=10, min_samples_leaf=5).fit(np.column_stack((x1_train, x2_train)), y_train)

    x1_a, x2_a, y_a = generate_data_t0(N=args.N, alpha=args.alpha, 
                                        beta=args.beta, omega1=args.omega1,
                                        omega2=args.omega2,
                                        omega3=args.omega3, gamma=args.gamma)
    # preds_a = model.predict_proba(np.column_stack((x1_a, x2_a)))[:, 1]

    # Dataset b (drift -> omega1 = -0.75)
    drift=-0.75
    x1_b, x2_b, y_b = generate_data_t0(N=args.N, alpha=args.alpha, 
                                        beta=args.beta, omega1=drift,
                                        omega2=args.omega2,
                                        omega3=args.omega3, gamma=args.gamma)
    # preds_b = model.predict_proba(np.column_stack((x1_b, x2_b)))[:, 1]
    model_b = None
    if model_class == 'lr':
        model_b = LogisticRegression(penalty=None).fit(np.column_stack((x1_b, x2_b)), y_b)
    else:
        model_b = DecisionTreeClassifier(max_depth=10, min_samples_split=10, min_samples_leaf=5).fit(np.column_stack((x1_b, x2_b)), y_b)

    
    # Dataset c (drift -> omega1 = 0.05)
    drift=0.05
    x1_c, x2_c, y_c = generate_data_t0(N=args.N, alpha=args.alpha, 
                                        beta=args.beta, omega1=drift,
                                        omega2=args.omega2,
                                        omega3=args.omega3, gamma=args.gamma)
    # preds_c = model.predict_proba(np.column_stack((x1_c, x2_c)))[:, 1]
    model_c = None
    if model_class == 'lr':
        model_c = LogisticRegression(penalty=None).fit(np.column_stack((x1_c, x2_c)), y_c)
    else:
        model_c = DecisionTreeClassifier(max_depth=10, min_samples_split=10, min_samples_leaf=5).fit(np.column_stack((x1_c, x2_c)), y_c)

    
    # Dataset d (drift -> omega1 = 0.75)
    drift=0.75
    x1_d, x2_d, y_d = generate_data_t0(N=args.N, alpha=args.alpha, 
                                        beta=args.beta, omega1=drift,
                                        omega2=args.omega2,
                                        omega3=args.omega3, gamma=args.gamma)
    # preds_d = model.predict_proba(np.column_stack((x1_d, x2_d)))[:, 1]
    model_d = None
    if model_class == 'lr':
        model_d = LogisticRegression(penalty=None).fit(np.column_stack((x1_d, x2_d)), y_d)
    else:
        model_d = DecisionTreeClassifier(max_depth=10, min_samples_split=10, min_samples_leaf=5).fit(np.column_stack((x1_d, x2_d)), y_d)


    # Plot pre deployment performance
    plot_average_predictions(X=np.column_stack((x1_a[:1000], x2_a[:1000])), y=y_a[:1000], clf=model_a, ax=axes[0, 0], title='Dataset A (omega=1)', decision_thresholds=None)
    plot_average_predictions(X=np.column_stack((x1_a[:1000], x2_a[:1000])), y=y_a[:1000], clf=model_b, ax=axes[0, 1], title='Dataset B (omega=-0.75)', decision_thresholds=None)
    plot_average_predictions(X=np.column_stack((x1_a[:1000], x2_a[:1000])), y=y_a[:1000], clf=model_c, ax=axes[1, 0], title='Dataset C (omega=0.05)', decision_thresholds=None)
    plot_average_predictions(X=np.column_stack((x1_a[:1000], x2_a[:1000])), y=y_a[:1000], clf=model_d, ax=axes[1, 1], title='Dataset D (omega=0.75)', decision_thresholds=None)
    
    plt.savefig('data_drift_visualized_dt.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_model(training_strategy, model_class, x1, x2, y, y_swm=None, alert_triggered_swm=None, swm_weights=None,
                 A=None, perfect_weights=None, misspecified_weights=None, alert_triggered=None):
    model = None
    if model_class == 'lr':
        model = LogisticRegression(penalty=None)
    else:
        model = DecisionTreeClassifier(max_depth=10, min_samples_split=10, min_samples_leaf=5)

    if training_strategy == 'standard':
        model = model.fit(np.column_stack((x1, x2)), y)

    elif training_strategy == 'swm':
        model = model.fit(np.column_stack((
                            x1[~alert_triggered_swm],
                            x2[~alert_triggered_swm])), 
                        y_swm[~alert_triggered_swm], 
                        sample_weight=swm_weights[~alert_triggered_swm])
    
    elif training_strategy == 'awm_perfect':
        model = model.fit(np.column_stack((
                        x1[~np.logical_and(A == 1, alert_triggered)],
                        x2[~np.logical_and(A == 1, alert_triggered)])), 
                        y[~np.logical_and(A == 1, alert_triggered)], 
                        sample_weight=perfect_weights[~np.logical_and(A == 1, alert_triggered)])
    
    elif training_strategy == 'awm_misspecified':
        model = model.fit(np.column_stack((
                        x1[~np.logical_and(A == 1, alert_triggered)],
                        x2[~np.logical_and(A == 1, alert_triggered)])), 
                        y[~np.logical_and(A == 1, alert_triggered)], 
                        sample_weight=misspecified_weights[~np.logical_and(A == 1, alert_triggered)])
    return model

def get_metrics(monitoring_type, y, preds, y_swm=None, alert_triggered_swm=None, swm_weights=None,
                alert_triggered=None, A=None, perfect_weights=None, misspecified_weights=None):
    if monitoring_type == 'standard':
        metrics = standard_monitoring(y, preds)
    elif monitoring_type == 'swm':
        metrics = sampling_weighted_monitoring(
            y_swm[~alert_triggered_swm], preds[~alert_triggered_swm],
            swm_weights[~alert_triggered_swm])
    elif monitoring_type == 'awm_perfect':
        metrics = adherence_weighted_monitoring(
            y[~np.logical_and(A == 1, alert_triggered)],
            preds[~np.logical_and(A == 1, alert_triggered)],
            perfect_weights[~np.logical_and(A == 1, alert_triggered)])
    elif monitoring_type == 'awm_misspecified':
        metrics = adherence_weighted_monitoring(
            y_swm[~np.logical_and(A == 1, alert_triggered)],
            preds[~np.logical_and(A == 1, alert_triggered)],
            misspecified_weights[~np.logical_and(A == 1, alert_triggered)])
    return metrics

def save_metrics(results, name, monitoring_type, metrics, std_only=False):
    if len(results[name][monitoring_type]) > 0:
        for key, val in metrics.items():
            results[name][monitoring_type][key].append(val)
    else:
        for key, val in metrics.items():
            results[name][monitoring_type][key] = [val]
    
    if std_only:
        for key in ['awm_perfect', 'awm_misspecified', 'swm']:
            if name == 'm1_t0':
                results[name][key] = {key : results[name]['standard'][key] for key in metrics.keys()}
            else:
                results[name][key] = {key : np.nan for key in metrics.keys()}
def get_preds(model, x1, x2):
    preds = model.predict_proba(np.column_stack((x1, x2)))[:, 1]
    return preds

def get_weight_vals(x1, x2, y, u1, alert_triggered, alert_triggered_swm, A):    
    x = np.column_stack((x1[alert_triggered], x2[alert_triggered]))
    u1 = u1[alert_triggered]
    A_triggered = A[alert_triggered]
    perfect_preds, misspecified_preds = fit_propensity_model(x, u1, A_triggered)
    perfect_weights = np.ones_like(y)  
    misspecified_weights = np.ones_like(y)  
    perfect_weights[alert_triggered] = 1 / (1 - perfect_preds)
    misspecified_weights[alert_triggered] = 1 / (1 - misspecified_preds)
    withheld_alert = (alert_triggered != alert_triggered_swm)
    swm_weights = np.ones_like(y) * args.pi_s
    swm_weights[withheld_alert] = 1 / args.withholding_prob

    return {'perfect_weights': perfect_weights, 
            'misspecified_weights': misspecified_weights, 
            'swm_weights': swm_weights, 
            }

def create_modified_data(model, N=args.N, omega1=args.omega1):
    x1, x2, y, y_swm, A, u1, alert_triggered, alert_triggered_swm = \
    generate_data_t1_t2(model, 
        delta=args.delta, N=N, alpha=args.alpha, beta=args.beta, omega1=omega1,
        omega2=args.omega2, omega3=args.omega3, gamma=args.gamma, phi1=args.phi1, phi2=args.phi2,
        eta=args.eta, mu=args.mu, sigma=args.sigma, pi_s=args.pi_s, operation=args.operation,
        lambda_s=args.lambda_s, scenario='label_modification', withholding_prob=args.withholding_prob,
        adherence_constant=args.adhere_constant)
    return {
        'x1': x1,
        'x2': x2,
        'y': y,
        'y_swm': y_swm,
        'A': A,
        'u1': u1,
        'alert_triggered': alert_triggered,
        'alert_triggered_swm': alert_triggered_swm,
    }

def create_basic_data(N=args.N, omega1=args.omega1):
    x1, x2, y = generate_data_t0(N=N, alpha=args.alpha, 
                                        beta=args.beta, omega1=omega1,
                                        omega2=args.omega2,
                                        omega3=args.omega3, gamma=args.gamma)
    return {
        'x1': x1,
        'x2': x2,
        'y': y
    }

def wrapper_metrics_weighted(result_model, result_data, result_name, results):
    preds = get_preds(result_model, result_data['x1'], result_data['x2'])
    weights = get_weight_vals(result_data['x1'], result_data['x2'], result_data['y'], result_data['u1'],
                    result_data['alert_triggered'], result_data['alert_triggered_swm'], result_data['A'])
    for m_type in mon_types:
        metrics = get_metrics(m_type, y=result_data['y'], preds=preds, 
                                y_swm=result_data['y_swm'], alert_triggered_swm=result_data['alert_triggered_swm'], 
                                alert_triggered=result_data['alert_triggered'], A=result_data['A'], 
                                swm_weights=weights['swm_weights'], perfect_weights=weights['perfect_weights'], 
                                misspecified_weights=weights['misspecified_weights'])
        save_metrics(results, name=result_name, monitoring_type=m_type, metrics=metrics)

def wrapper_weighted_model(result_data, model_class, models, model_name, training_strategy):
    weights = get_weight_vals(result_data['x1'], result_data['x2'], result_data['y'], result_data['u1'],
                        result_data['alert_triggered'], result_data['alert_triggered_swm'], result_data['A'])
    models[model_name] = create_model(training_strategy=training_strategy, model_class=model_class, x1=result_data['x1'],
                                x2=result_data['x2'], y=result_data['y'],
                                y_swm=result_data['y_swm'], alert_triggered_swm=result_data['alert_triggered_swm'], 
                                swm_weights=weights['swm_weights'], A=result_data['A'], 
                                perfect_weights=weights['perfect_weights'], 
                                misspecified_weights=weights['misspecified_weights'], 
                                alert_triggered=result_data['alert_triggered'])
        
def wrapper_metrics_standard(result_model, result_data, result_name, results):
    metrics = get_metrics(
            monitoring_type='standard', y=result_data['y'], 
            preds=get_preds(result_model, result_data['x1'], result_data['x2'])
            )
    save_metrics(results, name=result_name, monitoring_type='standard', metrics=metrics, std_only=True)

def simulate():
    data = { 
        't0_train': {}, # data as is, used to train 1st model
        't0': {}, # data as is (silent deployment of 1st model)
        't1': {}, # feedback effect caused by 1st model, 
        't1_samp2': {}, #another sample of t1
        't2': {}, # feedback effect caused by 1st model + data shift
        'v0_train': {}, # used to train M2 (data drift)
        'v0': {},  # used to test (data drift)
        't3_std': {}, # data drift + feedback effect caused by M3 trained in this way
        't3_awm': {}, # ""
        't3_awm_mis': {}, # ""
        't3_swm': {} # ""
    }

    # Different models and what strategy was used to train or re-train them
    models = {
        'm1': None,
        'm2': None,
        'm3_std': None,
        'm3_swm': None,
        'm3_awm_perfect': None,
        'm3_awm_misspecified': None,
        'm4_std': None
    }   

    results = {
    'm1_t0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm1_t1': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm1_t2': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm':{}},
    'm1_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm':{}}, 
    'm2_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm':{}}, 
    'm3_std_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_std_t3_std': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_swm_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_swm_t3_swm': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_awm_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_awm_t3_awm': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_awm_mis_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm3_awm_mis_t3_awm_mis': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_t1_samp2': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_t0_samp2': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}}, 
    'm4_std_t0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_t1': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_z1': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_t0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_t1': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_t2': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}},
    'm4_std_v0': {'standard': {}, 'awm_perfect': {}, 'awm_misspecified': {}, 'swm': {}}
    }

    model_class = 'dt'
    mon_types = ['standard', 'awm_perfect', 'awm_misspecified', 'swm']
    drift = 0.05

    for _ in tqdm(range(100)):
        # Create t0_train
        data['t0_train'] = create_basic_data()

        # Create m1
        models['m1'] = create_model(training_strategy='standard', model_class=model_class, 
                                    x1=data['t0_train']['x1'], x2=data['t0_train']['x2'], 
                                    y=data['t0_train']['y'])
        
        # Create t0
        data['t0'] = create_basic_data()
        wrapper_metrics_standard(models['m1'], data['t0'], 'm1_t0', results)

        # Create t1 (feedback caused by m1)
        data['t1'] = create_modified_data(model=models['m1'])

        # Create t1_train
        data['t1_train'] = create_modified_data(model=models['m1'])
        wrapper_metrics_weighted(models['m1'], data['t1'], 'm1_t1', results)

        # Create t2 (feedback caused by m1 + drift)
        data['t2'] = create_modified_data(model=models['m1'], omega1=drift)
        wrapper_metrics_weighted(models['m1'], data['t2'], 'm1_t2', results)

        # Create v0_train
        data['v0_train'] = create_basic_data(omega1=drift)

        # Create v0
        data['v0'] = create_basic_data(omega1=drift)
        wrapper_metrics_standard(models['m1'], data['v0'], 'm1_v0', results)

        # Create m2
        result_data = data['v0']
        models['m2'] = create_model(training_strategy='standard', model_class=model_class, x1=result_data['x1'],
                                    x2=result_data['x2'], y=result_data['y'])
        wrapper_metrics_standard(models['m2'], data['v0'], 'm2_v0', results)

        ## STANDARD VERSION
        # Create m3_std (retrain m1 on t2)
        result_data = data['t2']
        models['m3_std'] = create_model(training_strategy='standard', model_class=model_class, x1=result_data['x1'],
                                    x2=result_data['x2'], y=result_data['y'])
        wrapper_metrics_standard(models['m3_std'], data['v0'], 'm3_std_v0', results)

        # Create t3_std (feedback caused by m3_std + data drift)
        result_model = models['m3_std']
        data['t3_std'] = create_modified_data(model=result_model, omega1=drift)
        wrapper_metrics_weighted(models['m3_std'], data['t3_std'], 'm3_std_t3_std', results)
        
        ## SWM VERSION
        # Create m3_swm (retrain m1 on t2)
        # result_data = data['t2']

        wrapper_weighted_model(data['t2'], 'swm', models)
        wrapper_metrics_standard(models['m3_swm'], data['v0'], 'm3_swm_v0', results)

        # Create t3_swm (feedback caused by m3_swm + data drift)
        result_model = models['m3_swm']
        data['t3_swm'] = create_modified_data(model=result_model, omega1=drift)
        wrapper_metrics_weighted(models['m3_swm'], data['t3_swm'], 'm3_swm_t3_swm', results )

        ## AWM VERSION
        # Create m3_awm (retrain m1 on t2)
        # result_data = data['t2']

        wrapper_weighted_model(data['t2'], 'awm', models)
        wrapper_metrics_standard(models['m3_awm'], data['v0'], 'm3_awm_v0', results)

        # Create t3_awm (feedback caused by m3_awm + data drift)
        result_model = models['m3_awm']
        data['t3_awm'] = create_modified_data(model=result_model, omega1=drift)
        wrapper_metrics_weighted(models['m3_awm'], data['t3_awm'], 'm3_awm_t3_awm', results)

        ## AWM_Mis VERSION
        # Create m3_awm_mis (retrain m1 on t2)
        # result_data = data['t2']

        wrapper_weighted_model(data['t2'], 'awm_mis', models)
        wrapper_metrics_standard(models['m3_awm_mis'], data['v0'], 'm3_awm_mis_v0', results)

        # Create t3_awm_mis (feedback caused by m3_awm_mis + data drift)
        result_model = models['m3_awm_mis']
        data['t3_awm_mis'] = create_modified_data(model=result_model, omega1=drift)
        wrapper_metrics_weighted(models['m3_awm_mis'], data['t3_awm_mis'], 'm3_awm_mis_t3_awm_mis', results)

        # Create m4_std
        result_data = data['t1']
        models['m4_std'] = create_model(training_strategy='standard', model_class=model_class,
                                        x1=result_data['x1'], x2=result_data['x2'], y=result_data['y'])
        
        # Create z1
        result_model = models['m4_std']
        data['z1'] = create_modified_data(model=result_model)
        wrapper_metrics_standard(models['m4_std'], data['t0'], 'm4_std_t0', results)

        # Results: m4_std on z1
        wrapper_metrics_weighted(models['m4_std'], data['z1'], 'm4_std_z1', results)

        # Results: m4_std on t2
        wrapper_metrics_weighted(models['m4_std'], data['t2'], 'm4_std_t2', results)

        # Results: m4_std on t1
        wrapper_metrics_weighted(models['m4_std'], data['t1'], 'm4_std_t1', results)

        # Results: m4_std on v0
        wrapper_metrics_standard(models['m4_std'], data['v0'], 'm4_std_v0', results)

    # plot_names = ['m1_t0', 'm1_t1', 'm1_t2', 'm4_std_t0', 'm4_std_z1', 'm4_std_t2', 'm4_std_t1', 
    #               'm3_std_v0', 'm3_awm_v0', 'm3_awm_mis_v0', 'm3_swm_v0', 
    #               'm3_std_t3_std', 'm3_awm_t3_awm', 'm3_awm_mis_t3_awm_mis', 'm3_swm_t3_swm']
    
    # ground_truths = ['m1_t0', 'm1_t0', 'm1_v0', 'm4_std_t0', 'm4_std_t0', 'm4_std_v0', 'm4_std_t0',
    #                  'm2_v0', 'm2_v0', 'm2_v0', 'm2_v0',
    #                   'm3_std_v0', 'm3_awm_v0', 'm3_awm_mis_v0', 'm3_swm_v0']

    # plot_names = ['m3_std_v0', 'm3_awm_v0', 'm3_awm_mis_v0', 'm3_swm_v0', 
    #               'm3_std_t3_std', 'm3_awm_t3_awm', 'm3_awm_mis_t3_awm_mis', 'm3_swm_t3_swm']
    
    # ground_truths = ['m3_std_v0', 'm3_awm_v0', 'm3_awm_mis_v0', 'm3_swm_v0',
    #                   'm3_std_v0', 'm3_awm_v0', 'm3_awm_mis_v0', 'm3_swm_v0']

    plot_names = ['m2_v0']
    ground_truths = ['m2_v0']

    for plot_name, gt in zip(plot_names, ground_truths):
        ground_truth = results[gt]['standard']
        plot_results_revamped(plot_name=plot_name, results=results[plot_name], ground_truth=ground_truth, save_fig=True)



def main():
    # visualize_data()
    # simulate()

    # save simulation results in a pickle to open later and load plots
    with open('Pickles/results.pickle', 'rb') as handle:
        results = pickle.load(handle)
    plot_timeline(results, save_fig=False)
    plot_retraining_strategy_effect(results, save_fig=False)
    plot_retraining_early_effect(results, save_fig=False)

if __name__ == '__main__':
    main()
