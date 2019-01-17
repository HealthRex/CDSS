
import unittest
import medinfo.ml.SupervisedLearner as SupervisedLearner
import SupervisedLearnerTestData

class TestSupervisedClassifier(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_no_patient_leak(self):
        processed_matrix = SupervisedLearnerTestData.processed_matrix

        X_train, _, X_test, _ = SupervisedLearner.train_test_split(
            processed_matrix, outcome_label="all_components_normal")

        patIds_train = X_train.pop('pat_id').values.tolist()
        patIds_test = X_test.pop('pat_id').values.tolist()
        self.assertFalse(set(patIds_train) & set(patIds_test))





