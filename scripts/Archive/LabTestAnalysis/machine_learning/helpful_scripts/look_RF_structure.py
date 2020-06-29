


from sklearn.externals import joblib
from sklearn.tree import export_graphviz

lab = 'ALK'
data_source = 'UMich'
lab_type = 'component'
data_folderpath = '../data-%s-component-10000-episodes/%s/' % (data_source, lab)

rf_model = joblib.load(data_folderpath + "%s-normality-random-forest-model.pkl"%lab)._model

# rf_model = joblib.load('Uric-Acid, Serum - Plasma-normality-random-forest-model.pkl')._model

print(len(rf_model.feature_importances_))

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
fm_io = FeatureMatrixIO()
df_processed = fm_io.read_file_to_data_frame(data_folderpath + '%s-normality-matrix-processed.tab'%lab)
# df_processed = fm_io.read_file_to_data_frame('Uric Acid, Serum - Plasma-normality-test-matrix-processed_byStanford.tab')
df_processed.pop('pat_id')

if lab_type == 'panel':
    df_processed.pop('all_components_normal')
else:
    df_processed.pop('component_normal')
cols = df_processed.columns.values.tolist()

estimator = rf_model.estimators_[5]

export_graphviz(estimator, out_file='tree.dot',
                feature_names = cols,
                class_names = ['abnormal', 'normal'],
                rounded = True, proportion = False,
                precision = 2, filled = True)

import pydot

(graph,) = pydot.graph_from_dot_file('tree.dot')
print(graph)
graph.write_png('tree.png')


# from subprocess import call
# call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png'])

# import matplotlib.pyplot as plt
# plt.savefig('visual_rf.png')