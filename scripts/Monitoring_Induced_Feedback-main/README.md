# Monitoring_Induced_Feedback
Simulate different monitoring and retraining strategies post deployment of machine learning model. Assess strategy effectiveness under feedback drift and data drift.

Run simulate.py to simulate various scenarios the machine learning model might encounter post deployment and gather the ground truth model performance & estimated performance using standard unweighted, sampling weighted, and adherence weighted estimation approaches. Use simulate.py to plot performance and visualize how changing key parameters affects the type of data drift induced. Simulate.py uses helper functions from monitoring.py and data_generation.py.

The data from the simulations can be found under Pickles/results.pickle.

Code Contributors: Grace Y.E. Kim and Conor K. Corbin  
