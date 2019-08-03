# To Run Configuration File:

1) go to 'configuration.py'
  a) set recommender_path to your box sync folder: clinical_recommender_pipeline
  b) set database connection for recommender
2) run script 'python clinicalRecommenderTests.py' (unit testing for folders)
3) run script 'python tracker_script_v4.py'
4) run script 'python tracker_script_v5.py'
5) go to 'oneClick.py'
  a) set path to tracker_script_results for v4 and v5 (subsequent testing would all be v5)
6) run script 'python oneClick.py'
