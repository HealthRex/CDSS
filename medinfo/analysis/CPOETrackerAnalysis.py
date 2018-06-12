import sys, os
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from optparse import OptionParser
import csv

class SimulationAnalyzer:
	def __init__(self, data_file):
		self.data_file = data_file
		self.load_tracker_data()

	def load_tracker_data(self):
		with open(self.data_file, 'r') as fp:
			json_data = json.load(fp)
			self.event_tracker_data = json.loads(json_data['eventTracker'])
			self.results_tracker_data = json.loads(json_data['resultsTracker'])
			self.signed_item_tracker_data = json.loads(json_data['signedItemsTracker'])
			self.user = json_data['user']
			self.patient = json_data['patient']
			self.start_time = json_data['startTime']
			self.end_time = json_data['endTime']

	def number_mouse_clicks_all(self):
		"""Aggregate the number of mouse clicks on buttons and inputs on page"""
		event_tracker = self.event_tracker_data
		clicks = self.number_mouse_clicks(filters=event_tracker.keys(), perc=False)

		return clicks

	def number_mouse_clicks(self, filters=[], perc=False):
		"""Aggregate number of mouse clicks on particular buttons and inputs on page

		Args:
			filters (list): names of events to count
			perc (bool): whether to return frequency of clicks as percentage (of total clicks)
		"""
		event_tracker = self.event_tracker_data
		clicks = 0.
		for event in filters:
			try:
				event_ocurrences = len(event_tracker[event])
				clicks += event_ocurrences
			except Exception as e:
				continue
		if perc:
			total_clicks = self.number_mouse_clicks_all()
			percentage = clicks / total_clicks
			return percentage

		return clicks

	def click_summary(self, perc=False):
		"""Compute click summary for each event

		Args:
			perc (bool): whether to return event click summaries as percentages (of total clicks)
		Return:
			summary (dict): dict mapping event to frequency or percentage (based on perc)
		"""
		summary = dict()
		event_tracker = self.event_tracker_data
		for event in event_tracker.keys():
			summary[event] = self.number_mouse_clicks(filters=[event], perc=perc)

		return summary

	def convert_timestamp(self, ms_timestamp):
		"""Convert millisecond timestamp to (hours, minutes, seconds)"""
		seconds=(ms_timestamp/1000)%60
		seconds = int(seconds)
		minutes=(ms_timestamp/(1000*60))%60
		minutes = int(minutes)
		hours=(ms_timestamp/(1000*60*60))%24

		return (hours, minutes, seconds)

	def elapsed_time(self):
		"""Compute total time spent on case"""
		elapsed_time_millis = int(self.end_time) - int(self.start_time)
		hours, minutes, seconds = self.convert_timestamp(elapsed_time_millis)

		return ("%d:%d:%d" % (hours, minutes, seconds))

	def total_orders(self, unique=False):
		"""Aggregate total number of signed orders

		Args:
			unique (bool): if set to True, duplicate orders will be ignored
		"""
		signed_items = self.retrieve_signed_orders(unique=unique)
		count = len(signed_items)

		return count

	def retrieve_signed_orders(self, batch=False, unique=False):
		"""Return all signed order items

		Args:
			batch (bool): whether to preserve the groups in which orders appear
			unique (bool): if set to True, duplicate orders will be ignored, but
						   if batch is set to True, only duplicates within the batch will
						   be ignored. Note: Using unique=True will unpreserve
						   the order in which signed orders appear.
		"""
		signed_items_tracker = self.signed_item_tracker_data
		signed_items = []
		for timestamp in signed_items_tracker.keys():
			signed_items_batch = signed_items_tracker[timestamp]
			if batch:
				if unique:
					signed_items_batch = list(set(signed_items_batch))
				signed_items.append(signed_items_batch)
			else:
				signed_items += signed_items_batch

		if unique and not batch:
			signed_items = list(set(signed_items))

		return signed_items


	def total_recommendations(self, unique=True):
		"""Aggregate total number of recommendations

		Args:
			unique (bool): if set to True, duplicate recommendations will be ignored
		"""
		# Recommender specifically triggered when search is '' and by Find Orders when search query is ''
		count = self.total_search_results(search_modes=["", "FindOrders"], search_query="", unique=unique)

		return count


	def total_search_results(self, search_modes=[], search_query=None, unique=True):
		"""Aggregate total number of results for particular search modes

		Args:
			search_modes (iterable): search actions of {"", "FindOrders", "OrderSets",
									 "Diagnoses"} to filter by.
			search_query (str): search query used for result (substring matching is used)
			unique (bool): if set to True, duplicate results are ignored
		"""
		if not search_modes:
			search_modes = self.results_tracker_data.keys()
		results = self.retrieve_results(search_modes=search_modes, search_query=search_query, batch=False, unique=unique)
		count = len(results)

		return count


	def retrieve_results(self, search_modes=[], search_query=None, batch=False, unique=True):
		"""Return results for particular search modes

		Args:
			search_modes (iterable): search actions of {"", "FindOrders", "OrderSets",
									 "Diagnoses"} to filter by.
			search_query (str): search query used for result (substring matching is used)
			batch (bool): whether to preserve the groups in which recommendations appear
			unique (bool): if set to True, duplicate recommendations will be ignored,
						   if batch is set to True, only duplicates within each batch will
						   be ignored. Note: Using unique=True will unpreserve
						   the order in which recommendations appear.
		"""
		results_tracker = self.results_tracker_data
		if not search_modes:
			search_modes = results_tracker.keys()
		results = []
		for mode in search_modes:
			try:
				mode_results = results_tracker[mode]
				for obj in mode_results:
					state = obj['state']
					#	  Wild card search 					Recommendations search											Other results search
					if (search_query is None) or (search_query == "" and state['searchQuery'] == "") or (search_query != "" and search_query in state['searchQuery']):
						items = obj['items']
						for data_type in items.keys():
							items_list = items[data_type]
							# Extract item ids
							items_list = list(map(lambda item: item.split('|')[0], items_list))
							if batch:
								if unique:
									# Remove duplicates within batch
									items_list = list(set(items_list))
								results.append(items_list)
							else:
								results += items_list
			except Exception as e:
				print(e)
				continue

		if unique and not batch:
			results = list(set(results))

		return results


	def number_signed_in_recommended(self, perc=False):
		"""Number of signed orders that appear in recommender
		Args:
			perc (bool): whether to return frequency as percentage (over all signed orders)
		"""
		signed_orders = self.retrieve_signed_orders(unique=True, batch=False)
		recommendations = self.retrieve_results(search_modes=[""], batch=False, unique=True)
		intersection = set(signed_orders) & set(recommendations)
		count = len(intersection)
		if perc:
			count = float(count) / len(signed_orders)

		return count

	def construct_timeline(self):
		"""Flatten trackers and order all events by timestamp"""
		# Flatten eventTracker
		event_tracker = self.event_tracker_data
		events = []
		for event_name in event_tracker.keys():
			for event_ocurrence in event_tracker[event_name]:
				event_time = event_ocurrence['eventTime']
				events.append((event_time, event_name, event_ocurrence))
		# Sort events by timestamp
		sorted_events = sorted(events, key=lambda x: x[0])
		return sorted_events

	def visualize_timeline(self, timeline):
		"""Draw timeline

		Args:
			timeline (iterable): iterable of tuples (position, name, info_dict)
		"""
		times = list(map(lambda x: datetime.datetime.fromtimestamp((x[0] - timeline[0][0])/1000.0), timeline))
		names = list(map(lambda x: x[1], timeline))
		names_unique = sorted(list(set(list(map(lambda x: x, names)))))


		norm = plt.Normalize(1,4)
		c = np.random.randint(1,5,size=len(names_unique))
		cmap = plt.cm.inferno
		fig, ax = plt.subplots(figsize=(15,4))

		ax.yaxis.set_visible(False)
		ax.spines['right'].set_visible(False)
		ax.spines['left'].set_visible(False)
		ax.spines['top'].set_visible(False)
		ax.xaxis.set_ticks_position('bottom')

		ax.get_yaxis().set_ticklabels([])
		ms = pd.to_timedelta("1", unit='ms')
		plt.xlim(times[0] - 5*ms, times[-1] + 5*ms)

		plots = []

		for i, name in enumerate(names_unique):
			named_events = list(filter(lambda x: x[1] == name, timeline))
			named_times = list(map(lambda x: datetime.datetime.fromtimestamp((x[0] - timeline[0][0])/1000.0), named_events))
			sc = plt.scatter(named_times, [i*5+1]*len(named_times), marker='o', s=100, alpha=0.8)
			plots.append(sc)

		ax.legend(plots, names_unique)
		plt.show()


def aggregate_simulation_data(data_home, output_path, append_to_existing=False, source_path=None):
	"""Generate 'flat' csv file or append to existing csv file from directory of simulation (json) files

	Args:
		data_home (str): path to directory containing simulation json files
		output_path (str): path to where csv file should be saved to
		append_to_existing (bool): whether to append aggregated data from data_home to existing csv file
		source_path (str): if append_to_existing is True, source_path is path to used csv file
	"""
	# Filter out files that do not end with .json
	filenames = filter(lambda f: f.endswith('.json'), os.listdir(data_home))
	# Append directory path to filenames
	filenames = list(map(lambda f: os.path.join(data_home, f), filenames))
	headers = ["user", "patient", "start_time", "elapsed_time", "num_clicks", "total_orders", "num_signed_in_recommended"]
	if not append_to_existing:
		# Create initial csv file
		with open(output_path,'w') as out_csv:
			file_writer = csv.writer(out_csv)
			file_writer.writerow(headers)
		source_path = output_path
	# Use same logic as appending to existing (now that there is an initial csv to append to)
	with open(source_path, 'a') as out_csv:
		file_writer = csv.writer(out_csv)
		for filename in filenames:
			print("Processing {}".format(filename))
			fields = []
			# Instantiate SimulationAnalyzer for current data file
			siman = SimulationAnalyzer(filename)
			# Add current base metrics
			fields.append(siman.user)
			fields.append(siman.patient)
			fields.append(siman.start_time)
			fields.append(siman.elapsed_time())
			fields.append(siman.number_mouse_clicks_all())
			fields.append(siman.total_orders())
			fields.append(siman.number_signed_in_recommended())
			file_writer.writerow(fields)

			# Delete SimulationAnalyzer to free any useless memory
			del siman


def main(argv):
	parser = OptionParser()
	parser.add_option("-f", "--file",  dest="data_file", help="JSON file containing collected data.")
	parser.add_option("-a", "--agg", dest="aggregate", help="Create aggregate csv file?")
	parser.add_option("-d", "--agg_home", dest="data_home", help="path to directory containing simulation json files")
	parser.add_option("-o", "--agg_output", dest="output_path", help="path to where csv file should be saved to")
	parser.add_option("-s", "--agg_source", dest="source_path", help="source_path is path to existing csv file to append to")
	options, args = parser.parse_args(argv[1:])

	if not options.aggregate:
		siman = SimulationAnalyzer(options.data_file)
		print("Total mouse clicks: ", siman.number_mouse_clicks_all())
		print("Click summary: ", siman.click_summary(perc=False))
		print("Elapsed time: ", siman.elapsed_time())
		print("Total signed orders: ", siman.total_orders())
		print("Signed order ids: ", siman.retrieve_signed_orders())
		print("Signed order batches:", siman.retrieve_signed_orders(batch=True))
		print("Total recommendations: ", siman.total_recommendations())
		print("Recommendation ids: ", siman.retrieve_results(search_modes=["", "FindOrders"], batch=False, search_query=""))
		print("Recommendation batches: ", siman.retrieve_results(search_modes=["", "FindOrders"], batch=True, search_query=""))
		print("Signed/Recommended overlap: ", siman.number_signed_in_recommended())
		print("Total results:", siman.total_search_results())
		print("Timeline data: ", siman.construct_timeline())
		print("Timeline view: ", siman.visualize_timeline(siman.construct_timeline()))
	else:
		data_home = options.data_home
		output_path = options.output_path
		append_to_existing = False
		source_path = None
		if options.source_path:
			append_to_existing = True
			source_path = options.source_path
		aggregate_simulation_data(data_home, output_path, append_to_existing=append_to_existing, source_path=source_path)



if __name__ == '__main__':
	main(sys.argv)
