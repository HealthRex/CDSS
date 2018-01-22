#!/usr/bin/python
"""
Abstract class for an end-to-end pipeline which builds a raw feature matrix,
processes the raw matrix, trains a predictor on the processed matrix,
tests the predictor's performance, and summarizes its analysis.

SubClasses will be expected to override the following functions:
* __init__()
* _add_features()
* _remove_features()
* _select_features()
* summarize()
"""

class SupervisedLearningPipeline:
    def __init__():
        pass

    def _add_features():
        pass

    def _remove_features():
        pass

    def _select_features():
        pass

    def summarize():
        pass
