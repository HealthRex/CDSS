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
        default='./experiments/run0/',
        help='where to save results'
    )
    parser.add_argument(
        '--model_path',
        default='./model_info/label_HCT_deploy.pkl',
        help='where the model lives'
    )
    parser.add_argument(
        '--label_path',
        default='./model_info/label_HCT_yhats',
        help='where the test set labels and predictions live'
    )
    parser.add_argument(
        '--feature_path',
        default='./model_info/test_features.npz',
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
    worst_aucs_null = []
    if args.compare_to_random_partition:
        for i in tqdm(range(args.n_null)):
            indices = [idx for idx in range(len(labels))]
            indices_shuffled = np.random.choice(indices, size=len(indices),
                replace=False)
            labels_random = [labels[idx] for idx in indices_shuffled]
            predictions_random = [predictions[idx] for idx in indices_shuffled]
            clf = tree.DecisionTreeRegressor(max_depth=5, min_samples_leaf=100)
            worst_auc, _ = partition_performance(
                attributes=features,
                labels=labels_random,
                predictions=predictions_random,
                clf=clf
            )
            worst_aucs_null.append(worst_auc)

    # Get worst performance with with recursive partitioning
    clf = tree.DecisionTreeRegressor(max_depth=5, min_samples_leaf=100)
    worst_auc, _ = partition_performance(
        attributes=features,
        labels=labels,
        predictions=predictions,
        clf=clf
    )

    # Plot actual value againts null distribution
    len_n = len(worst_aucs_null)
    pvalue = len([p for p in worst_aucs_null if p <= worst_auc]) / len_n
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax = sns.histplot(x=worst_aucs_null, bins=20, stat='count', ax=ax)
    ax.plot([worst_auc, worst_auc], [0, ax.get_ylim()[1]], color='black',
        label=f"Worst Parition auc={round(worst_auc, 2)} p < {pvalue}")
    ax.set_title("Worst partition performance vs null")
    ax.set_xlabel("Worst AUC")
    ax.set_ylabel("Frequency")
    ax.legend()
    os.makedirs(args.outpath, exist_ok=True)
    outfig = os.path.join(args.outpath, 'worst_auc_comparison.png')
    plt.savefig(outfig, bbox_inches='tight', dpi=300)

def partition_performance(attributes, labels, predictions, clf, 
        get_worst_path=False):
    """
    Performs the feature partioning and returns data for logging 
    """
    worst_path = None
    ppart = PerformancePartitioner(
        attributes=attributes,
        labels=labels,
        predictions=predictions,
        clf=clf
    )
    ppart.partition()
    ppart.evaluate()
    
    # Get partition with worst performance
    worst_partition = ppart.df_partition_scores.sort_values('auc').head(1)
    worst_auc = worst_partition['auc']

    if get_worst_path:
        worst_parition_indices = [int(a) for a in 
                                worst_partition['samples'].split('-')]
        X_worst_partition = ppart.attributes[worst_parition_indices]
        worst_path = ppart.get_paths_for_sample(
            X_test=X_worst_partition
        )
    return float(worst_auc.values[0]), worst_path

if __name__ == '__main__':
    main()
