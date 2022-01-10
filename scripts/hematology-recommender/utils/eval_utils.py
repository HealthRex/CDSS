# -*- coding: utf-8 -*-
import os
from sklearn.metrics import precision_recall_curve

def evaluate(preds, targets, k=10, thresh=0.5):
    """
    Metric calculating multilabel precision@k and recall@k given the threshold
    preds: (a x N) matrix with scores for each of the N classes
    targets: (a x N) binary matrix with expected groundtruth per class
    """
    # see link could be helpful, metrics are implemented
    # https://github.com/facebookresearch/mmf/blob/322bd33d4a67f5bbe806624d9afd3c2cf921ec50/mmf/modules/metrics.py#L1020
    # TODO: extend for multilabel case

    return precision, recall