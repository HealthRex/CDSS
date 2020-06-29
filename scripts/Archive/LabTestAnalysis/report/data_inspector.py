

'''
inspect how many patients overlap
'''

from sklearn.model_selection import train_test_split
# TODO: previous import
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
import pandas as pd
from scripts.LabTestAnalysis.machine_learning import LabNormalityPredictionPipeline
import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'
import matplotlib.pyplot as plt

folder = '../machine_learning/data/'
labs = LabNormalityPredictionPipeline.NON_PANEL_TESTS_WITH_GT_500_ORDERS

if False:
    all_testset_leakage_percentages = []
    all_best_aucrocs = []
    for lab in labs:

        try:
            raw_matrix_file = '%s-normality-matrix-10000-episodes-raw.tab'%lab
            fm_io = FeatureMatrixIO()
            raw_matrix = fm_io.read_file_to_data_frame(folder+'/'+lab+'/'+raw_matrix_file)

            row, col = raw_matrix.shape

            from medinfo.ml.SupervisedClassifier import SupervisedClassifier
            algs = SupervisedClassifier.SUPPORTED_ALGORITHMS

            best_aucroc = 0
            for alg in algs:
                report_file = '%s-normality-prediction-%s-report.tab'%(lab,alg)
                report_df = pd.read_csv(folder+'/'+lab+'/'+alg+'/'+report_file, sep='\t')
                best_aucroc = max(report_df['roc_auc'].values[0], best_aucroc)

            all_best_aucrocs.append(best_aucroc)


            random_state = 123456789
            train_inds, test_inds = train_test_split(raw_matrix['pat_id'], random_state=random_state)

            train_inds_set = set(train_inds)
            appeared_cnt = 0
            for ind in test_inds:
                if ind in train_inds_set:
                    appeared_cnt += 1
            leakage_percent = float(appeared_cnt)/len(test_inds)
            all_testset_leakage_percentages.append(leakage_percent)

            print("lab: %s, best auc: %.4f, leakage percent: %.3f"% (lab, best_aucroc, leakage_percent))
        except Exception as e:
            print(e)
            pass

all_testset_leakage_percentages = [0.6828, 0.9018645731108931, 0.6929824561403509, 0.7156, 0.8268275372604684, 0.3291566265060241, 0.9376, 0.9244, 0.8488085456039441, 0.8505564387917329, 0.7557251908396947, 0.6801909307875895, 0.7998483699772555, 0.994, 0.7189605389797883, 0.882, 0.9262782401902497, 0.6185831622176592, 0.8268, 0.6727019498607242, 0.5701149425287356, 0.5793103448275863, 0.9480122324159022, 0.6268, 0.8318965517241379, 0.25689404934687954, 0.4926992073425115, 0.9216, 0.7832699619771863, 0.20176082171680118, 0.4482463644140291, 0.8021390374331551, 0.6819461198230801, 0.5650118203309693, 0.9364, 0.9996, 0.21914893617021278, 0.9952, 0.9856, 0.9952, 0.9776, 0.9971949509116409, 0.8184, 0.9705760464152507, 0.9968, 0.996, 0.778, 0.7108, 0.878, 0.833409821018816, 0.4057971014492754, 0.25476190476190474, 0.792, 0.996, 0.7232, 0.9964, 0.7581573896353166, 0.9924, 0.8288431061806656, 0.8218579234972677, 0.5926161680458307, 0.9336, 0.28085106382978725, 0.5303983228511531, 0.984, 0.4762357414448669, 0.9344, 0.5632, 0.550253807106599, 0.8739352640545145, 0.8258064516129032, 0.3124470787468247, 0.9876, 0.8885644768856448, 0.9912]
all_best_aucrocs = [0.77537, 0.83006000000000002, 0.64549999999999996, 0.89767999999999992, 0.75961999999999996, 0.68588000000000005, 0.64273000000000002, 0.66517999999999999, 0.62936999999999999, 0.65083999999999997, 0.89617000000000002, 0.75588999999999995, 0.85387000000000002, 0.75636999999999999, 0.65939999999999999, 0.94871000000000005, 0.81633, 0.71088999999999991, 0.86601000000000006, 0.74753000000000003, 0.77808999999999995, 0.74602000000000002, 0.81026999999999993, 0.78943999999999992, 0.77303999999999995, 0.78813, 0.78274999999999995, 0.81415999999999999, 0.75697999999999999, 0.60846, 0.68961000000000006, 0.57347999999999999, 0.77385000000000004, 0.69881000000000004, 0.90137999999999996, 0.79401999999999995, 0.49775000000000003, 0.79413, 0.89322000000000012, 0.89478999999999997, 0.95248999999999995, 0.82766000000000006, 0.82577000000000012, 0.90326000000000006, 0.81774999999999998, 0.90883999999999998, 0.78312999999999999, 0.82441000000000009, 0.91690000000000005, 0.83013999999999999, 0.75601000000000007, 0.79541000000000006, 0.76278999999999997, 0.78643999999999992, 0.89736000000000005, 0.90612000000000004, 0.64054999999999995, 0.89373999999999998, 0.60760000000000003, 0.60661999999999994, 0.80069999999999997, 0.85952000000000006, 0.62736999999999998, 0.72450000000000003, 0.93898999999999999, 0.65133999999999992, 0.86272000000000004, 0.61850000000000005, 0.92010999999999998, 0.68474000000000002, 0.62549999999999994, 0.64343000000000006, 0.96214, 0.70689999999999997, 0.77383999999999997]

plt.scatter(all_testset_leakage_percentages, all_best_aucrocs)
plt.xlabel("percentage of leakage")
plt.ylabel("auc roc")

for lab, x, y in zip(labs, all_testset_leakage_percentages, all_best_aucrocs):
    plt.annotate(
        lab[3:],
        xy=(x, y))
plt.savefig('leakage-holdout.png')