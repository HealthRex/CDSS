import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score, precision_score, \
average_precision_score, brier_score_loss
import matplotlib.pyplot as plt

class ModelWrapper():

    def __init__(self, model):
        self.model = model
    def fit(self, X, y, sample_weight=None):
        nan_mask = ~np.isnan(y)
        X = X[nan_mask]
        y = y[nan_mask]
        if sample_weight is not None:
            sample_weight = sample_weight[nan_mask]
        self.model.fit(X, y, sample_weight=sample_weight)

def calculate_auroc(y_true, y_pred, sample_weight=None):
    return roc_auc_score(y_true, y_pred, sample_weight=sample_weight)

def calculate_ece(y_true, y_pred, sample_weight=None, n_bins=10):
    return expected_calibration_error(y_true, y_pred, b_bins=n_bins, sample_weight=sample_weight)

def calculate_sensitivity(y_true, y_pred, sample_weight=None):
    y_pred = np.where(y_pred > 0.5, 1, 0)
    return recall_score(y_true, y_pred, pos_label=1, sample_weight=sample_weight)

def calculate_specificity(y_true, y_pred, sample_weight=None):
    y_pred = np.where(y_pred > 0.5, 1, 0)
    return recall_score(y_true, y_pred, pos_label=0, sample_weight=sample_weight)

def calculate_precision(y_true, y_pred, sample_weight=None):
    y_pred = np.where(y_pred > 0.5, 1, 0)
    return precision_score(y_true, y_pred, sample_weight=sample_weight)

def calculate_accuracy(y_true, y_pred, sample_weight=None):
    y_pred = np.where(y_pred > 0.5, 1, 0)
    return accuracy_score(y_true, y_pred, sample_weight=sample_weight)

def calculate_average_precision(y_true, y_pred, sample_weight=None):
    return average_precision_score(y_true, y_pred, sample_weight=sample_weight)

def calculate_brier_score(y_true, y_pred, sample_weight=None):
    return brier_score_loss(y_true, y_pred, sample_weight=sample_weight)

def calculate_f1(y_true, y_pred, sample_weight=None):
    y_pred = np.where(y_pred > 0.5, 1, 0)
    precision = precision_score(y_true, y_pred, sample_weight=sample_weight)
    recall = recall_score(y_true, y_pred, sample_weight=sample_weight)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1

# Updated monitoring functions to return a dictionary of metrics
def standard_monitoring(y_true, y_pred):
    # Create a mask to filter out examples with np.nan in y_true
    nan_mask = ~np.isnan(y_true)

    # Apply the mask to y_true and y_pred
    y_true = y_true[nan_mask]
    y_pred = y_pred[nan_mask]

    return {
        'AUROC': calculate_auroc(y_true, y_pred),
        'ECE': calculate_ece(y_true, y_pred),
        'Sensitivity': calculate_sensitivity(y_true, y_pred),
        'Specificity': calculate_specificity(y_true, y_pred),
        'Precision': calculate_precision(y_true, y_pred),
        'Accuracy': calculate_accuracy(y_true, y_pred),
        'Brier score': calculate_brier_score(y_true, y_pred),
        'F1': calculate_f1(y_true, y_pred),
        'Avg Precision': calculate_average_precision(y_true, y_pred)
    }

def adherence_weighted_monitoring(y_true, y_pred, weights):
    # Create a mask to filter out examples with np.nan in y_true
    nan_mask = ~np.isnan(y_true)

    # Apply the mask to y_true and y_pred
    y_true = y_true[nan_mask]
    y_pred = y_pred[nan_mask]
    weights = weights[nan_mask]

    return {
        'AUROC': calculate_auroc(y_true, y_pred, sample_weight=weights),
        'ECE': calculate_ece(y_true, y_pred, sample_weight=weights),
        'Sensitivity': calculate_sensitivity(y_true, y_pred, sample_weight=weights),
        'Specificity': calculate_specificity(y_true, y_pred, sample_weight=weights),
        'Precision': calculate_precision(y_true, y_pred, sample_weight=weights),
        'Accuracy': calculate_accuracy(y_true, y_pred, sample_weight=weights),
        'Brier score': calculate_brier_score(y_true, y_pred, sample_weight=weights),
        'F1': calculate_f1(y_true, y_pred, sample_weight=weights),
        'Avg Precision': calculate_average_precision(y_true, y_pred, sample_weight=weights)
    }

def sampling_weighted_monitoring(y_true, y_pred, weights):
    # Create a mask to filter out examples with np.nan in y_true
    nan_mask = ~np.isnan(y_true)

    # Apply the mask to y_true and y_pred
    y_true = y_true[nan_mask]
    y_pred = y_pred[nan_mask]
    weights = weights[nan_mask]

    return {
        'AUROC': calculate_auroc(y_true, y_pred, sample_weight=weights),
        'ECE': calculate_ece(y_true, y_pred, sample_weight=weights),
        'Sensitivity': calculate_sensitivity(y_true, y_pred, sample_weight=weights),
        'Specificity': calculate_specificity(y_true, y_pred, sample_weight=weights),
        'Precision': calculate_precision(y_true, y_pred, sample_weight=weights),
        'Accuracy': calculate_accuracy(y_true, y_pred, sample_weight=weights),
        'Brier score': calculate_brier_score(y_true, y_pred, sample_weight=weights),
        'F1': calculate_f1(y_true, y_pred, sample_weight=weights),
        'Avg Precision': calculate_average_precision(y_true, y_pred, sample_weight=weights)
    }

def expected_calibration_error(labels, predictions, b_bins=5, sample_weight=None):
    """
    Computes the expected calibration error (ECE) of a model. Implemented for
    binary classification only.
    """

    # Put labels and predictions into a dataframe
    df = pd.DataFrame(data={
        'y_true': labels,
        'y_prob': predictions,
        'sample_weight': sample_weight
    })

    # Create bins by dividing probability space into equal width bins.
    bins = np.linspace(0.0, 1.0, b_bins + 1)
    
    # Apply bin id to each row of dataframe
    binids = np.searchsorted(bins[1:-1], df['y_prob'])
    df['bin_id'] = binids

    # Loop over groups of bin_id and compute accuracy, confidence, and counts
    import pdb
    bin_accs, bin_confs, bin_counts = [], [], []
    for bin_id, group in df.groupby('bin_id'):
        if sample_weight is not None:
            sw = group['sample_weight'].values
        else:
            sw = sample_weight
        bin_acc = accuracy_score(group['y_true'], group['y_prob'] > 0.5,
                                 sample_weight=sw)
        bin_conf = max(np.average(group['y_prob'], weights=sw),
                       np.average(1-group['y_prob'], weights=sw))
        bin_count = len(group) if sample_weight is None else np.sum(sw)
        bin_accs.append(bin_acc)
        bin_confs.append(bin_conf)
        bin_counts.append(bin_count)

    # Compute expected calibration error
    bin_accs = np.asarray(bin_accs)
    bin_confs = np.asarray(bin_confs)
    bin_counts = np.asarray(bin_counts)
    ece = np.sum(bin_counts * np.abs(bin_accs - bin_confs)) / np.sum(bin_counts)
    return ece

def plot_average_predictions(X, y, clf, ax, title, grid_size=1000, decision_thresholds=[0.5]):
    # Set up the grid
    x_min, x_max = X[:, 0].min() - 0.1, X[:, 0].max() + 0.1
    y_min, y_max = X[:, 1].min() - 0.1, X[:, 1].max() + 0.1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, grid_size), np.linspace(y_min, y_max, grid_size))

    # Predict probabilities on the grid
    Z = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
    Z = Z.reshape(xx.shape)

    # Plot the average predictions as a gradient
    contour = ax.contourf(xx, yy, Z, cmap='RdBu', alpha=0.5)
    colorbar = plt.colorbar(contour, ax=ax)
    colorbar.set_label('Average Prediction in Region', fontsize=12)

    # Plot the decision boundary
    if decision_thresholds is not None:
        for decision_threshold in decision_thresholds:
            ax.contour(xx, yy, Z, levels=[decision_threshold], colors='red', linewidths=3, linestyles='solid')
    # ax.clabel(boundary, inline=1, fontsize=10, fmt=f'Decision Boundary ({decision_threshold:.2f})')
 
    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, marker='x', cmap='RdBu', edgecolors='k')
    ax.set_xlabel('X1')
    ax.set_ylabel('X2')
    ax.set_title(title)
    
def plot_results_revamped(plot_name, results, ground_truth, save_fig=False):
    # results = {'standard': [], 'awm_perfect': [], 'awm_misspecified': [], 'swm': []}
    # Define the monitoring types and their labels for plotting
    monitoring_types = ['standard', 'awm_misspecified', 'awm_perfect', 'swm']
    monitoring_labels = ["Standard", "AWM (Confounded)", 'AWM', "SWM"]
    metrics = ['Accuracy', 'AUROC', 'Avg Precision', 'Brier score', 'ECE', 'F1', 
               'Precision', 'Sensitivity', 'Specificity']

    # Create a figure
    fig, axs = plt.subplots(3, 3, figsize=(20, 15))

    # Create dictionary of axs xlimits based on metric type
    xlimits = {
        'AUROC': [0, 1.0],
        'ECE': [0.0, 0.5],
        'F1': [0, 1.0],
        'Brier score': [0, 0.5],
        'Sensitivity': [0, 1.0],
        'Specificity': [0, 1.0],
        'Precision': [0, 1.0],
        'Accuracy': [0, 1.0],
        'Avg Precision': [0, 1.0]
    }

    # Define color palette and styles
    colors = ['navy', 'darkgreen', 'maroon', 'steelblue']
    marker_styles = ['o', 's', 'D', '^']  # Different marker for each monitoring type

    for ax_index, metric in enumerate(metrics):
        row_index = ax_index // 3
        col_index = ax_index % 3
        ax = axs[row_index, col_index]
        
        # Plot each monitoring type's performance
        for i, monitoring in enumerate(monitoring_types):
            # val = results[monitoring][metric]
            performances = np.array([results[monitoring][metric]])
            valid_performances = performances[~np.isnan(performances)]
            y_pos = i  # Y position for the current monitoring type
            if len(valid_performances) > 0:
                mean = np.mean(valid_performances)
                percentile_2_5 = np.percentile(valid_performances, 2.5)
                percentile_97_5 = np.percentile(valid_performances, 97.5)

                # Error bars
                error = [[mean - percentile_2_5], [percentile_97_5 - mean]]

                # Plot the point and error bar
                ax.errorbar(mean, y_pos, xerr=error, fmt=marker_styles[i], color=colors[i], 
                            ecolor=colors[i], linestyle='-', capsize=5)

        # Plot one vertical dashed line for ground truth
        gt_performances = np.array(ground_truth[metric])
        valid_gt_performances = gt_performances[~np.isnan(gt_performances)]
        ax.axvline(x=np.mean(valid_gt_performances), color='gray', linestyle='dashed', label='Ground Truth')

        # Set labels and title
        ax.set_yticks(range(len(monitoring_types)))
        if ax_index in [0, 3, 6]:
            ax.set_yticklabels(monitoring_labels)
        else:
            ax.set_yticklabels([''] * len(monitoring_types))
        ax.set_xlabel(metric)
        ax.set_title(f"{metric} by Monitoring Strategy")
        ax.invert_yaxis()  # Invert y-axis so that the first entry is at the top
        ax.set_xlim(xlimits[metric])
        ax.grid(True)

        if ax_index in [2]:
            ax.legend(loc='lower left') # bbox_to_anchor=(1.55, 1.05)) # prev lower left

    plt.suptitle(f"Performance Metrics Estimated by Monitoring Strategy of {plot_name}", fontsize=32)
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    if save_fig:
        plt.savefig(f'fig4_{plot_name}.png', dpi=300, bbox_inches='tight')
    # plt.show()

def plot_timeline(results, save_fig=False):
    monitoring_types = ['standard', 'awm_misspecified', 'awm_perfect', 'swm']
    monitoring_labels = ["Standard", "AWM (Confounded)", 'AWM', "SWM"]
    monitoring_names = ['std', 'awm_mis', 'awm', 'swm']

    # Create a figure
    metric = 'AUROC'
    fig, axs = plt.subplots(2, 2, figsize=(20,10))
    fig.subplots_adjust(hspace=0.5) #, hspace=5)wspace=3

    for j, mon_type in enumerate(monitoring_types):
        plot_names = ['m1_t0', 'm1_t2', f'm3_{monitoring_names[j]}_v0', f'm3_{monitoring_names[j]}_t3_{monitoring_names[j]}']
        ground_truth_names = ['m1_t0', 'm1_v0', f'm3_{monitoring_names[j]}_v0', f'm3_{monitoring_names[j]}_v0']

        print(f"MONITORING TYPE: {mon_type}")
        print(f"PLOT NAMES: {plot_names}")
        print(f"GROUND TRUTH NAMES: {ground_truth_names}")

        baseline = 0
        gts = []
        row_index = j // 2
        col_index = j % 2
        ax = axs[row_index][col_index]

        AUC_scores = []

        for i, result_name in enumerate(plot_names):
            print(f"PLOT NAME: {result_name}")
            if result_name == f'm3_{monitoring_names[j]}_v0' and mon_type != 'standard':
                performances = np.array([results[result_name]['standard'][metric]])
            else:
                performances = np.array([results[result_name][mon_type][metric]])
            valid_performances = performances[~np.isnan(performances)]
            if len(valid_performances) > 0:
                mean = np.mean(valid_performances)
                print(f"MEAN VALUE: {mean}")
                percentile_2_5 = np.percentile(valid_performances, 2.5)
                percentile_97_5 = np.percentile(valid_performances, 97.5)

                # Error bars
                error = [[mean - percentile_2_5], [percentile_97_5 - mean]]
                color='navy'
                if i < 2:
                    color = 'gray'
                ax.errorbar(y=mean, x=i, yerr=error, fmt='o', color=color, linestyle='-', capsize=5)
                AUC_scores += [round(mean, 2)]

                if i == 0: baseline = mean

            gt_performances = np.array(results[ground_truth_names[i]]['standard'][metric])
            valid_gt_performances = gt_performances[~np.isnan(gt_performances)]
            mean_gt = np.mean(valid_gt_performances)
            gts += [mean_gt]
            print(f"Mean GT: {mean_gt} ADDED TO GTS")
        
        print("-----")
    
        for num, val in enumerate(AUC_scores):
            ax.text(x=num, y=val-0.1, s=f"{val}", ha='center', fontsize='x-small')

        ax.axhline(baseline, color='green', linestyle='dashed', label='Original Model on Original Data')
        ax.plot([0, 1, 2, 3], gts, color='darkseagreen', linestyle='dashed', label='Ground Truth')
        
        ax.axvspan(0, 1.5, alpha=0.3, color='gray', label='Original Model')
        ax.axvspan(1.5, 3, alpha=0.3, color='navy', label='Retrained Model')
        
        ax.set_xticks([0, 1, 2, 3])

        ax.set_xticklabels([
        'Silent Deployment: \n Original Model', 
        'Loud Deployment (Feedback)\n + Drift: Original Model', 
        'Silent Deployment\n + Drift: Retrained Model', 
        'Loud Deployment (Feedback)\n + Drift: Retrained Model'])
        
        ax.tick_params(axis='both', which='major', labelsize=10)
        ax.set_ylabel('Estimated AUROC', fontsize=12)
        ax.set_xlabel('Dataset', fontsize=12)
        ax.set_ylim([0, 1.0])
        ax.legend(loc='lower right', prop={'size': 10})
        ax.set_title(f'{monitoring_labels[j]} Monitoring & Retraining Strategy')
    
    if save_fig:
        plt.savefig(f'Timeline_final2.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_retraining_strategy_effect(results, save_fig=False):
    x = range(4)
    y_vals = []
    error_bars = []
    
    for name in ['m3_std_v0', 'm3_swm_v0', 'm3_awm_v0', 'm3_awm_mis_v0']:
        performances = np.array([results[name]['standard']['AUROC']])
        valid_performances = performances[~np.isnan(performances)]
        if len(valid_performances) > 0:
            mean = np.mean(valid_performances)
            percentile_2_5 = np.percentile(valid_performances, 2.5)
            percentile_97_5 = np.percentile(valid_performances, 97.5)

            # Error bars
            error = [[mean - percentile_2_5], [percentile_97_5 - mean]]
            error_bars += [error]
            
            y_vals += [mean]
        
    colors = ['navy', 'darkgreen', 'maroon', 'steelblue']
    marker_styles = ['o', 's', 'D', '^']  # Different marker for each monitoring type

    plt.plot(x, y_vals, linestyle="", marker='o')
    for i, error in enumerate(error_bars):
        plt.errorbar(y=y_vals[i], x=i, yerr=error, fmt='o', color='darkseagreen', linestyle='-', capsize=5)
    
    performances = np.array([results['m1_t0']['standard']['AUROC']])
    valid_performances = performances[~np.isnan(performances)]
    if len(valid_performances) > 0:
        mean = np.mean(valid_performances)
    plt.hlines(y=mean, xmin=min(x), xmax=max(x), linestyle='dashed', color='gray', label="Original Model on Original Data")

    performances = np.array([results['m2_v0']['standard']['AUROC']])
    valid_performances = performances[~np.isnan(performances)]
    if len(valid_performances) > 0:
        mean = np.mean(valid_performances)
    plt.hlines(y=mean, xmin=min(x), xmax=max(x), linestyle='dashed', color='green', label="New Model Trained \n Exclusively on Drift Data")

    performances = np.array([results['m1_t2']['standard']['AUROC']]) #m1_v0
    valid_performances = performances[~np.isnan(performances)]
    if len(valid_performances) > 0:
        mean = np.mean(valid_performances)
    plt.hlines(y=mean, xmin=min(x), xmax=max(x), linestyle='dashed', color='red', label="Original Model on Original Data \n with Drift + Feedback")
    
    
    
    plt.legend(loc='lower right', prop={'size': 10})
    plt.xticks(ticks=range(4), labels=["Standard", "SWM", 'AWM', "AWM (Confounded)"])
    plt.xlabel('Retraining Strategy', fontsize=12)
    plt.ylabel('Estimated AUROC of Retrained Model \n On Drift Data', fontsize=12)
    plt.tick_params(axis='x', which='major', labelsize=10)
    plt.ylim([0, 1.0])
    plt.title("Effect of Retraining Strategy")

    for num, val in enumerate(y_vals):
        plt.text(x=num, y=val-0.1, s=f"{round(val, 2)}", ha='center', fontsize='x-small')

    if save_fig:
        plt.savefig(f'Retraining_strategy_effect3.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_retraining_early_effect(results, save_fig=False):
    x = range(6)
    y_vals, error_bars = [], []

    for name in ['m1_t0', 'm1_t1', 'm4_std_t1', 'm4_std_t0', 'm4_std_z1', 'm4_std_z2']:
        performances = np.array([results[name]['standard']['AUROC']])
        valid_performances = performances[~np.isnan(performances)]
        if len(valid_performances) > 0:
            mean = np.mean(valid_performances)
            percentile_2_5 = np.percentile(valid_performances, 2.5)
            percentile_97_5 = np.percentile(valid_performances, 97.5)

            # Error bars
            error = [[mean - percentile_2_5], [percentile_97_5 - mean]]
            error_bars += [error]
            
            y_vals += [mean]

    plt.plot(x, y_vals, linestyle="", marker='o')
    for i, error in enumerate(error_bars):
        color='navy'
        if i < 2:
            color = 'gray'
        plt.errorbar(y=y_vals[i], x=i, yerr=error, fmt='o', color=color, linestyle='-', capsize=5)
    
    plt.axvspan(0, 2, alpha=0.3, color='gray', label='Original Model')
    plt.axvspan(2, 5, alpha=0.3, color='navy', label='Retrained Model')

    plt.legend(loc='upper right', prop={'size': 10})
    plt.xticks(ticks=range(6), labels=["Silent Deployment: \n Original Model", 
                                       "Loud Deployment (Feedback): \n Original Model", 
                                       'Testing New Model on Data From \n Original Model Feedback', 
                                       'Silent Deployment: \n Retrained Model', 
                                       'Loud Deployment (Feedback):\n Retrained Model', 
                                       'Loud Deployment (Feedback) + Drift:\n  Retrained Model']
                                       )
    plt.xlabel('Dataset', fontsize=12)
    plt.title('Effect of Early Retraining')
    plt.ylabel('Estimated AUROC', fontsize=12)
    plt.tick_params(axis='both', which='major', labelsize=10)
    plt.ylim([0, 1.0])

    for num, val in enumerate(y_vals):
        plt.text(x=num, y=val-0.1, s=f"{round(val, 2)}", ha='center', fontsize='x-small')

    if save_fig:
        plt.savefig(f'Retraining_early_effect4.png', dpi=300, bbox_inches='tight')
    plt.show()
