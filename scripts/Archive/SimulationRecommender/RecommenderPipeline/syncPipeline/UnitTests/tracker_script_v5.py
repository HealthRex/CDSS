import pandas as pd
import datetime
from CPOETrackerAnalysis import aggregate_simulation_data
from configuration import *

# setting date when saving
now = datetime.datetime.now()
date_string = str(now.year) + '_' + str(now.month) + '_' + str(now.day) + '_' + str(now.hour) + '_' + str(now.second) + '_'  

out_file = tracker_data + 'tracker_output/' + date_string + 'tracker_data_5.csv'  # Fill in with path to which csv output will be saved
data_home = tracker_data + 'v5_data'  # Fill in with path to directory containing v4 json files

# Run aggregator
aggregate_simulation_data(data_home, output_path=out_file)
print(date_string)
