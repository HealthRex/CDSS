### Define the PerformancePartitioner
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from sklearn import tree
from sklearn.metrics import mean_squared_error
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import average_precision_score
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from tqdm import tqdm

import pdb

"""
Detecting Weak Points in Clinical Risk Predction Models with Recursive
Partitioning. 

Section 1 of Paper:
    For k clincial prediction models (I'll train).
    Can PerformancePartitioner 
        1) find more extreme weakpoints than something that just randomly
        partitions the data into same number of partitions
        2) find more exteme weakpoints than an unsupervised clustering
        method that partions the data into same number of clusters

Section 2 of Paper:
    Implications on Domain Generalization.
        * Can use to estimate perforance on new population if you know the
          prevalance of each partition in new population (domain adapation).
        * Compare to inverse probability weighting
        * Can provide semantically meaningful explanations as to why a task
          may not be generalizing well to a new population. Ie prevalance
          in a low performing partition is higher. 

Section 3 of Paper:
    Implications on Fairness Evaluations
        * Can be used to evaluate fairness multi-dimensionally, alluding to
          intersectionality.
        * Test whether can find more extreme weakpoints that common fairness
          evaluation that assess performance across pre-specified
          protected subgroups.
"""

class PerformancePartitioner():
    """
    Definition of performance partitioner, houses logic that given attributes, 
    predicictions, and labels on a held out test set fits a decision tree that 
    partions the attribute space based on a particular scoring function, and
    then estimates model peformance in these regions.
    """
    
    def __init__(self, attributes, labels, predictions, clf,
                 scoring_function=euclidean, random_state=42):
        """
        Args:
            attributes: NxM matrix where N is the number of examples on test set
                 and M is number of attributes to partition performance on.
            labels: N length vector of labels in test set
            predictions: N length vector of predictions in test set
            scoring_function: a function that takes in a label and prediction 
                and returns a score
            performance_measure: a function that takea in labels and predicitons
                 and returns a model performance measure
        """
        self.attributes = attributes
        self.labels = np.array(labels)
        self.predictions = np.array(predictions)
        self.scoring_function = scoring_function
        self.clf = clf
        self.random_state=random_state
    
    def partition(self, tune=False):
        """
        Partions the attribute space into disjoint region that best separates
        result of the scoring function on the test set.  Sample half of the 
        data to fit the partions and uses the other half to estimate the 
        performance measure within each of the paritions.
        """
        self.scores = np.array([self.scoring_function(l, p) for l,p in 
                       zip(self.labels, self.predictions)])
        indices = [i for i in range(len(self.scores))]
        x_fit, self.x_est, s_fit, self.s_est, \
                inds_fit, self.inds_est = train_test_split(self.attributes, 
                                                           self.scores,
                                                           indices,
                                                           test_size=0.5,
                                                           random_state=42)
        auc_on_fit = roc_auc_score(self.labels[inds_fit], 
                                    self.predictions[inds_fit])
        auc_on_est = roc_auc_score(self.labels[self.inds_est],
                                    self.predictions[self.inds_est])

        if tune:
            self.cross_val_fit(X=x_fit, y=s_fit)
        else:
            self.clf.fit(X=x_fit, y=s_fit)

    def cross_val_fit(self, X, y):
        """
        Actually fit the decision tree and cross validate on the _fit set for
        model selection. We'll maintain certain constraints on the resulting
        partions, like a minimum number of examples required to be a leaf node.
        This will be toyed around with in experiments that will likely go 
        in appendix. 

        Args:
            X : attributes use generate partitions
            y : scoring function - ex the squared error between label and
                predicted probability of the model
        """
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=0.2,
            random_state=self.random_state)
        self.clf.fit(X_train, y_train)
        path = self.clf.cost_complexity_pruning_path(X_train, y_train)
        ccp_alphas, impurities = path.ccp_alphas, path.impurities
        mse_train, mse_val = [], []
        for a in tqdm(ccp_alphas):
            self.clf.ccp_alpha = a
            self.clf.fit(X_train, y_train)
            y_train_pred = self.clf.predict(X_train)
            y_val_pred = self.clf.predict(X_val)
            mse_train.append(mean_squared_error(y_train, y_train_pred))
            mse_val.append(mean_squared_error(y_val, y_val_pred))
        best_alpha = ccp_alphas[np.argmin(mse_val)]
        self.clf.ccp_alpha = best_alpha
        print(best_alpha)
        self.clf.fit(X_train, y_train)

        # cv = KFold(n_splits=1, random_state=self.random_state,
        #     shuffle=True)
        # max_alphas = 0
        # max_path = 0
        # for train_inds, test_inds in cv.split(X, y):
        #     self.clf.fit(X[train_inds], y[train_inds])
        #     path = self.clf.cost_complexity_pruning_path(
        #         X[train_inds], y[train_inds])
        #     ccp_alphas, impurities = path.ccp_alphas, path.impurities
        #     if max(ccp_alphas) > max_alphas:
        #         max_alphas = max(ccp_alphas)
        #     if len(ccp_alphas) > max_path:
        #         max_path = len(ccp_alphas)

        #     pdb.set_trace()
    
        # param_grid = {
        #     'max_depth': [3, 5, 10, 50, 100, None], 
        #     'min_samples_leaf' : 
        # }

    def evaluate(self):
        """
        Given a the fit partions, estimates scores among other model performance
        measures on evaluation set. 
        """
        x_est_nodes = self.clf.apply(self.x_est)
        df = pd.DataFrame(data={
            'leaf_node_idx': x_est_nodes,
            'scores': self.s_est,
            'predicted_scores' : self.clf.predict(self.x_est),
            'predictions': self.predictions[self.inds_est],
            'labels': self.labels[self.inds_est],
            'est_indices' : self.inds_est
        })
        node_idx_map = {}

        # Have to do this way because pandas does not support aggregation on 
        # multiple columns 
        groups = df.groupby('leaf_node_idx')
        self.num_groups = len(groups)
        for group in groups:
            node_idx_map[group[0]] = {}
            node_idx_map[group[0]]['score'] = group[1].scores.mean()
            node_idx_map[group[0]]['predicted_scores'] = group[1
                ].predicted_scores.mean() # will all be the same
            node_idx_map[group[0]]['n_samples'] = len(group[1])
            node_idx_map[group[0]]['prevalence'] = group[1].labels.mean()
            node_idx_map[group[0]]['ex_est_index'] = '-'.join([
                str(idx) for idx in group[1]['est_indices']])
            node_idx_map[group[0]]['accuracy'] = accuracy_score(
                group[1].labels, 
                [1 if p >= 0.5 else 0 for p in group[1].predictions])
            try:
                node_idx_map[group[0]]['average_precision'] = \
                    average_precision_score(group[1].labels,
                                            group[1].predictions)
            except:
                node_idx_map[group[0]]['average_precision'] = 999
            try:
                node_idx_map[group[0]]['auc'] = roc_auc_score(group[1].labels,
                    group[1].predictions)
            except:
                node_idx_map[group[0]]['auc'] = 999

        # All values will be same within group, hence take first
        self.df_partition_scores = df.assign(
            scores=lambda x: [node_idx_map[idx]['score'] for idx 
                              in x.leaf_node_idx],
            predicted_scores=lambda x: [node_idx_map[idx]['predicted_scores']
                                        for idx in x.leaf_node_idx],
            n_samples=lambda x: [node_idx_map[idx]['n_samples']
                                for idx in x.leaf_node_idx],
            prevalance=lambda x: [node_idx_map[idx]['prevalence']
                                 for idx in x.leaf_node_idx],
            auc=lambda x: [node_idx_map[idx]['auc'] for idx in x.leaf_node_idx],
            samples=lambda x: [node_idx_map[idx]['ex_est_index']
                                      for idx in x.leaf_node_idx],
            accuracy=lambda x: [node_idx_map[idx]['accuracy']
                                for idx in x.leaf_node_idx],
            average_precision=lambda x: [node_idx_map[idx]['average_precision']
                                         for idx in x.leaf_node_idx]
            ).groupby('leaf_node_idx').first().reset_index()

    def get_paths_for_samples(self, X_test):
        n_nodes = self.clf.tree_.node_count
        children_left = self.clf.tree_.children_left
        children_right = self.clf.tree_.children_right
        feature = self.clf.tree_.feature
        threshold = self.clf.tree_.threshold

        node_indicator = self.clf.decision_path(X_test)
        leaf_id = self.clf.apply(X_test)
        
        sample_id = 0
        # obtain ids of the nodes `sample_id` goes through, ie, row `sample_id`
        node_index = node_indicator.indices[
            node_indicator.indptr[sample_id] : node_indicator.indptr[
                sample_id + 1]
        ]

        print("Rules used to predict sample {id}:\n".format(id=sample_id))
        for node_id in node_index:
            # continue to the next node if it is a leaf node
            if leaf_id[sample_id] == node_id:
                continue

            # check if value of  split feature for sample 0 is below threshold
            if X_test[sample_id, feature[node_id]] <= threshold[node_id]:
                threshold_sign = "<="
            else:
                threshold_sign = ">"

            print(
                "decision node {node} : (X_test[{sample}, {feature}] = {value})"
                " {inequality} {threshold})".format(
                    node=node_id,
                    sample=sample_id,
                    feature=feature[node_id],
                    value=X_test[sample_id, feature[node_id]],
                    inequality=threshold_sign,
                    threshold=threshold[node_id],
                )
            )
        return None # implement visualization later

    def explain_tree(self):
        """
        Prints explanation of the partions geneated by the decision tree 
        """
        n_nodes = self.clf.tree_.node_count
        children_left = self.clf.tree_.children_left
        children_right = self.clf.tree_.children_right
        feature = self.clf.tree_.feature
        threshold = self.clf.tree_.threshold

        node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
        is_leaves = np.zeros(shape=n_nodes, dtype=bool)
        stack = [(0, 0)]  # start with the root node id (0) and its depth (0)
        while len(stack) > 0:
            # `pop` ensures each node is only visited once
            node_id, depth = stack.pop()
            node_depth[node_id] = depth

            # If the left and right child of a node is not the same we have a
            # split node
            is_split_node = children_left[node_id] != children_right[node_id]
            # If a split node, append left and right children and depth to
            # `stack` so we can loop through them
            if is_split_node:
                stack.append((children_left[node_id], depth + 1))
                stack.append((children_right[node_id], depth + 1))
            else:
                is_leaves[node_id] = True

        print(
            "The binary tree structure has {n} nodes and has "
            "the following tree structure:\n".format(n=n_nodes)
        )
        for i in range(n_nodes):
            if is_leaves[i]:
                print(
                    "{space}node={node} is a leaf node.".format(
                        space=node_depth[i] * "\t", node=i
                    )
                )
            else:
                print(
                    "{space}node={node} is a split node: "
                    "go to node {left} if X[:, {feature}] <= {threshold} "
                    "else to node {right}.".format(
                        space=node_depth[i] * "\t",
                        node=i,
                        left=children_left[i],
                        feature=feature[i],
                        threshold=threshold[i],
                        right=children_right[i],
                    )
                )


    
