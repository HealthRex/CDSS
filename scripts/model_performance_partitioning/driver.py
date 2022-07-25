# Main entry point for executing experiments
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import pickle
import os
from scipy.sparse import load_npz
from sklearn import tree
from tqdm import tqdm

sns.set_theme(style='white', font_scale=1.5)

from partition import PerformancePartitioner

import pdb

def main():
    parser = argparse.ArgumentParser(description='Experiment Driver')
    parser.add_argument(
        '--outpath',
        default='./experiments/run_bigger_test_set/',
        help='where to save results'
    )
    parser.add_argument(
        '--model_path',
        default='./20220629_model_info/label_HCT_deploy.pkl',
        help='where the model lives'
    )
    parser.add_argument(
        '--label_path',
        default='./20220629_model_info/label_HCT_yhats',
        help='where the test set labels and predictions live'
    )
    parser.add_argument(
        '--feature_path',
        default='./20220629_model_info/test_features.npz',
        help='where the test set features live'
    )
    parser.add_argument(
        '--compare_to_random_partition',
        action='store_true',
        help=('whether to compare PerformancePartioner to random partitioner'
              'that permutes to which feature vector a (prediction, label) pair' 
              'belongs')
    )
    parser.add_argument(
        '--random_state',
        default=42,
        type=int,
        help=('random seed')
    )
    parser.add_argument(
        '--n_null',
        default=1000,
        type=int,
        help=('size of null distribution')
    )
    args = parser.parse_args()
    np.random.seed(args.random_state)

    # Load model and model data
    with open(args.model_path, 'rb') as f:
        model_pkl = pickle.load(f)
    model = model_pkl['model']
    feature_order = model_pkl['feature_order']
    features = load_npz(args.feature_path).toarray()
    hats = pd.read_csv(args.label_path)
    labels = hats['labels']
    predictions = hats['predictions']

    # Build null distribution
    worst_metrics_null = {'auc' : [], 'accuracy' : [],
                          'average_precision' : [], 'num_groups' : []}
    if args.compare_to_random_partition:
        for i in tqdm(range(args.n_null)):
            indices = [idx for idx in range(len(labels))]
            indices_shuffled = np.random.choice(indices, size=len(indices),
                replace=False)
            labels_random = [labels[idx] for idx in indices_shuffled]
            predictions_random = [predictions[idx] for idx in indices_shuffled]
            clf = tree.DecisionTreeRegressor(min_samples_leaf=2)
            worst_partition = partition_performance(
                attributes=features,
                labels=labels_random,
                predictions=predictions_random,
                clf=clf,
                random_state=args.random_state
            )
            worst_metrics_null['auc'].append(worst_partition['auc'])
            worst_metrics_null['accuracy'].append(worst_partition['accuracy'])
            worst_metrics_null['average_precision'].append(
                worst_partition['average_precision'])
            worst_metrics_null['num_groups'].append(
                worst_partition['num_groups'])

    # Get worst performance with with recursive partitioning
    clf = tree.DecisionTreeRegressor(
        min_samples_leaf=2000)
        
#ccp_alpha=3.329391502327633e-05)

    worst_partition = partition_performance(
        attributes=features,
        labels=labels,
        predictions=predictions,
        clf=clf,
        random_state=args.random_state,
        tune=False
    )

    # Plot scatter
    metrics = ['scores', 'accuracy', 'auc', 'average_precision', ]
    fig, axs = plt.subplots(1, 4, figsize=(40, 10))
    for i, metric in enumerate(metrics):
        plot_partion_score_vs_metric(worst_partition['ppart'], metric, axs[i])
    os.makedirs(args.outpath, exist_ok=True)
    outfig = os.path.join(args.outpath, '2000_min_sample.png')
    plt.savefig(outfig, bbox_inches='tight', dpi=300)

    # Plot actual value againts null distribution
    
    if args.compare_to_random_partition:
        colors = sns.color_palette()
        fig, axs = plt.subplots(1, 4, figsize=(40, 10))
        counter = 0
        for ax, m in zip(axs, worst_metrics_null):
            plot_hist_and_value(value=worst_partition[m],
                                null_disrtibution=worst_metrics_null[m],
                                ax=ax,
                                metric=m,
                                color=colors[counter])
            counter += 1

        os.makedirs(args.outpath, exist_ok=True)
        outfig = os.path.join(args.outpath, 'compare_to_null.png')
        plt.savefig(outfig, bbox_inches='tight', dpi=300)

def plot_hist_and_value(value, null_disrtibution, ax, metric, color):
    """
    Plots histogram of null distribution and verticl line with actual
    value given a metric and ax
    """
    n = len(null_disrtibution)
    pvalue = len([p for p in null_disrtibution if p <= value]) / n
    ax = sns.histplot(x=null_disrtibution,
                      bins=20,
                      stat='count',
                      ax=ax,
                      color=color)
    ax.plot([value, value], 
            [0, ax.get_ylim()[1]],
            color='black',
            linestyle='--',
            label=f"Worst Parition auc={round(value, 2)} p < {pvalue}")
    ax.set_title(f"Discovered Worst {metric} vs Null Distribution")
    ax.set_xlabel(f"Worst {metric}")
    ax.set_ylabel("Count")
    ax.legend()

def plot_partion_score_vs_metric(ppart, metric, ax):
    """
    Given a fit PerformancePartitioner, plots the predicted scores within
    each partion vs the estimate scores in the parition. 
    
    Args:
        ppart: a fit PerformancePartitioner
        metric: which metric to plot againts fit score, can be 'scores', 'auc',
        'accuracy', 'average_precision'
    """ 
    colors = sns.color_palette("icefire", as_cmap=True)
    valid_inds = [i for i, val in enumerate((ppart.df_partition_scores[metric]))
        if val != 999]
    prevalences = [int(p * 255) for p in 
                   ppart.df_partition_scores.prevalance[valid_inds]]
    sizes = ppart.df_partition_scores.n_samples[valid_inds] / \
        max(ppart.df_partition_scores.n_samples[valid_inds]) * 200
    ax.scatter(ppart.df_partition_scores.predicted_scores[valid_inds],
               ppart.df_partition_scores[metric][valid_inds],
               c=[colors.colors[p] for p in prevalences],
               s=sizes)
    ax.set_title(f'Predicted Errors vs Actual {metric}')
    ax.set_xlabel("Fit Scores")
    ax.set_ylabel(f"Actual {metric}")

def partition_performance(attributes, labels, predictions, clf, 
        get_worst_path=False, random_state=42, tune=False):
    """
    Performs the feature partioning and returns data for logging 
    """
    worst_path = None
    ppart = PerformancePartitioner(
        attributes=attributes,
        labels=labels,
        predictions=predictions,
        clf=clf,
        random_state=random_state,
    )
    ppart.partition(tune=tune)
    ppart.evaluate()
    
    # Get partition with worst performance
    worst_partition = ppart.df_partition_scores.sort_values('auc').head(1)

    if get_worst_path:
        worst_parition_indices = [int(a) for a in 
                                worst_partition['samples'].split('-')]
        X_worst_partition = ppart.attributes[worst_parition_indices]
        worst_path = ppart.get_paths_for_sample(
            X_test=X_worst_partition
        )
    

    return {
        'auc': float(worst_partition['auc'].values[0]),
        'accuracy': float(worst_partition['accuracy'].values[0]),
        'average_precision': float(
            worst_partition['average_precision'].values[0]),
        'num_groups' : ppart.num_groups,
        'worst_path' : worst_path,
        'ppart' : ppart
    }

if __name__ == '__main__':
    main()
