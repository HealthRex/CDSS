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
		self.version = data_file.split('.')[0].split('_')[-1]  # Get tracker version from filename
		# assert(self.version in ['v4', 'v5'])
		self.load_tracker_data()
		self.results_collection = self.normalize_results()
		# If using older version of tracker data, will need to parse signed collection
		# differently
		if self.version in ['v4', 'v5']:
			self.signed_orders_collection = self.normalize_signed_orders()
		else:
			self.signed_orders_collection = self.normalize_signed_orders_older()

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

	def parse_result_item_into_dict(self, base_item_dict, item_str):
		""" Extract item's clinical_item_id, name, and description from item_str
		and insert into item dict based on base_item_dict.
		Args:
			base_item_dict (dict): dict containing base attributes for item
			item_str (str): string representation of item. Expected to be of
				form: 'clinical_item_id|name|description'
		Returns:
			result_item_dict (dict): dict representing item_str passed in and
				all other global attributes of the item
		"""
		# print(item_str)
		result_item_dict = dict(base_item_dict)
		attributes = list(item_str.split('|'))
		result_item_dict['clinicalItemId'] = attributes[0]
		result_item_dict['name'] = ""
		result_item_dict['description'] = ""
		if len(attributes) > 1:
			result_item_dict['name'] = attributes[1]
			result_item_dict['description'] = attributes[2]
		return result_item_dict

	def parse_signed_item_into_dict(self, item_dict, item_str):
		"""Extract item's attributes and insert into item_dict.
		Args:
			item_dict (dict): dict to which item attributes will be added
			item_str (str): string containing item's attributes. Expected to be
				of form: 'clinical_item_id|source|searchQuery|mode|list_idx'
		"""
		clinical_item_id, source, searchQuery, mode, list_idx = list(item_str.split('|'))
		item_dict['clinicalItemId'] = clinical_item_id
		# Rename source to match names used for result items
		if source == 'resultSpace1':
			source = u'commonOrders'
		elif source == 'resultSpace2':
			source = u'specificOrders'
		elif source == 'non-recommender':
			source = u'data'
		item_dict['source'] = source if source != 'undefined' else 'data'  # Quick fix for issue where order set items are not recorded correctly
		item_dict['searchQuery'] = searchQuery  # May be undefined due to issue where order set items are not correctly recorded
		item_dict['mode'] = mode if mode != 'undefined' else 'OrderSets'  # Quick fix for issue where order set items are not recorded correctly
		item_dict['listIndex'] = 1000 if list_idx == 'undefined' else int(list_idx)  # Quick fix for issue where order set items are not recorded correctly - set listIndex to something arbitarily high

	def normalize_results(self):
		"""Join all results into a single, 'flat' collection of result item dicts
		Returns:
			results (list): list of result item dicts
		"""
		results = []
		for mode in self.results_tracker_data.keys():
			for mode_object in self.results_tracker_data[mode]:
				base_result_item_dict = dict()
				items_collection = None
				base_result_item_dict['mode'] = mode
				for instance_collection_name in mode_object.keys():  # ['items', 'state']
					for attr_name in mode_object[instance_collection_name].keys():
						# If attribute is a list, then items have been found.
						if isinstance(mode_object[instance_collection_name][attr_name], list):
							# Store type of result [commonOrders, specificOrders, data]
							base_result_item_dict['source'] = attr_name
							# Store items for processing after all other attributes have been stored
							items_collection = mode_object[instance_collection_name][attr_name]
						else:
							# Store non-list value into item dict
							base_result_item_dict[attr_name] = mode_object[instance_collection_name][attr_name]
				# Process items
				for item_str in items_collection:
					result_item_dict = self.parse_result_item_into_dict(base_result_item_dict, item_str)
					# Store item dict into results
					results.append(result_item_dict)
		return results


	def normalize_signed_orders_older(self):
		"""
		Map signed items from older version of tracker data to their corresponding
		result items.
		Returns:
			signed_orders (list): list of signed order item dicts.
				Note that these item dicts will not contain some of the attributes
				found in the item dicts returned by `normalize_signed_orders`
		"""
		signed_orders = []
		# Construct signed order clinical ids set and signed order tuples
		signed_orders_id_set = set()
		signed_orders_tuples = []
		for timestamp in self.signed_item_tracker_data:
			for item_str in self.signed_item_tracker_data[timestamp]:
				signed_orders_id_set.add(item_str)
				signed_orders_tuples.append((int(timestamp), item_str))

		# Filter out result items that do not correspond to items signed
		filtered_results = list(filter(lambda r: r['clinicalItemId'] in signed_orders_id_set, self.results_collection))
		# For each signed item, find most likely result item
		for signed_order in signed_orders_tuples:
			# For each result item that has the same clinical id as the current
			# signed order AND a store_time < the signed_time of the current item,
			# compute timestamp delta (signed_time - store_time).
			min_delta = float('inf')
			best_result = None
			for potential_result in list(filter(lambda r: r['clinicalItemId'] == signed_order[1] and r['storeTime'] < signed_order[0], filtered_results)):
				delta = signed_order[0] - potential_result['storeTime']
				if delta < min_delta:
					min_delta = delta
					best_result = potential_result

			# Map current signed item to result item with smallest delta
			signed_item_dict = dict(potential_result)
			signed_item_dict['signedTime'] = signed_order[0]
			signed_orders.append(signed_item_dict)

		return signed_orders


	def normalize_signed_orders(self):
		"""Join all signed items into a single, 'flat' colleciton of signed item dicts
		Returns:
			signed_orders (list): list of of signed order item dicts
		"""
		signed_orders = []
		for timestamp in self.signed_item_tracker_data:
			for item_str in self.signed_item_tracker_data[timestamp]:
				signed_item_dict = dict()
				signed_item_dict['signedTime'] = timestamp
				self.parse_signed_item_into_dict(signed_item_dict, item_str)
				signed_orders.append(signed_item_dict)

		return signed_orders

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
							if not (type(items_list) is list): continue
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
		# Map signed_orders to their ids (to be intersected with recommendations)
		signed_orders_ids = list(map(lambda orders: orders.split('|')[0], signed_orders))
		intersection = set(signed_orders_ids) & set(recommendations)
		count = len(intersection)
		if perc:
			count = float(count) / len(signed_orders)

		return count

	def get_manually_searched_options(self):
		"""Get list of result items that were presented from a manual search
		Returns:
			results (list): list of item dicts corresponding to items that were
				shown after a manual search (not from recommender)
		"""
		results = list(filter(lambda item: item['mode'] != '' and item['searchQuery'] != '', self.results_collection))
		return results

	def get_recommended_options(self, include_related=True):
		"""Get list of result items that were presented by recommender
		Args:
			include_related (bool): whether to include items that were shown
				after clicking 'related' button for a particular clinical item
		Returns:
			results (list): list of item dicts corresponding to items that were
				shown by recommender
		"""
		filter_fn = (lambda item: item['mode'] == '' or item['searchQuery'] == '')
		if include_related:
			filter_fn = (lambda item: (item['mode'] == '' or item['searchQuery'] == '') or (item['mode'] == 'related'))
		results = list(filter(filter_fn, self.results_collection))
		return results

	def _merge_intersection_items(self, merged_dict, result_item):
		"""Merge the two dicts corresponding to intersection items
		Args:
			merged_dict (dict): base dict where attributes of result item will
				be merged into
			result_dict (dict): dict corresponding to result item
		"""
		merged_dict.update(result_item)  # Note that result listIndex will overwrite that in merged_dict!

	def _result_signed_intersection(self, result_items, signed_items, filter_fn):
		"""Get the intersection between result items and signed items
		Args:
			result_items (list): list of result item dicts
			signed_items (list): list of signed item dicts
			filter_fn (fn): filter function called on result, signed item pair,
				where evaluation to True results in items being considered
				compatible and 'merged'. This funciton should take two items,
				one result item and one signed item, as parameters
		Returns:
			intersection (list): list of merged item dicts of items that are
				in both item lists, according to provided filter function
		"""
		intersection = []
		for signed_item in signed_items:
			merged_dict = dict(signed_item)
			found = False
			for result_item in result_items:  # Use some form of binary search?
				if filter_fn(result_item, signed_item):
					self._merge_intersection_items(merged_dict, result_item)
					# Corresponding result item found, stop searching
					found = True
					break;
			if found:
				intersection.append(merged_dict)
		return intersection

	def get_signed_from_manual_search(self):
		"""Get item dicts for items that were signed from manual-search results
		Returns:
			signed_from_manual (list): list of item dicts that were signed from
			 	manually-searching
		"""
		# Define filter function for determining intersection
		# This function checks that result item and signed item have same
		# clinicalItemId, listIndex (though s_item index will be ahead), and location source        r_item listIndex starts from 1, but s_item listIndex starts from 0
		filter_fn = lambda r_item, s_item: r_item['clinicalItemId'] == s_item['clinicalItemId'] and r_item['listIndex'] == s_item['listIndex'] - 1 and r_item['source'] == s_item['source']

		if self.version == 'v5':  # version 5 of tracker correctly tracks order set items in results
			# Get manually-searched signed items
			manual_search_results = self.get_manually_searched_options()
			signed_from_manual = self._result_signed_intersection(manual_search_results, self.signed_orders_collection, filter_fn=filter_fn)
		# elif self.version == 'v4':  # versions 4 of the tracker only tracks item sources in the signed orders collection
		else:
			signed_from_manual = list(filter(lambda s_item: s_item['source'] == 'data', self.signed_orders_collection))
		return signed_from_manual

	def get_signed_from_recommended(self, include_related=True):
		"""Get item dicts for items that were signed from recommender results
		Args:
			include_related (bool): whether to include items that were shown
				after clicking 'related' button for a particular clinical item
		Returns:
			signed_from_manual (list): list of item dicts that were signed from
			 	recommender options
		"""
		# Define filter function for determining intersection
		# This function checks that result item and signed item have same
		# clinicalItemId, listIndex (though s_item index will be ahead), and location source
		filter_fn = lambda r_item, s_item: r_item['clinicalItemId'] == s_item['clinicalItemId'] and (r_item['listIndex'] == s_item['listIndex'] - 1 or r_item['listIndex']+1 == s_item['listIndex'] - 1) and r_item['source'] == s_item['source']

		if self.version == 'v5':  # version 5 of tracker correctly tracks order set items in results
			# Get recommended signed items
			recommended_results = self.get_recommended_options(include_related=include_related)
			signed_from_recommended = self._result_signed_intersection(recommended_results, self.signed_orders_collection, filter_fn)
		# elif self.version == 'v4':  # versions 4 of the tracker only tracks item sources in the signed orders collection
		else:
			signed_from_recommended = list(filter(lambda s_item: s_item['source'] != 'data', self.signed_orders_collection))
		return signed_from_recommended

	def get_signed_missed_recommended(self, include_related=True):
		"""Get item dicts for items that were signed from manual-search results,
		but had appeared previously from recommended results
		Args:
			include_related (bool): whether to include items that were shown
				after clicking 'related' button for a particular clinical item
		Returns:
			missed_items (list): list of item dicts that appeared from the
				recommender, but were ultimately chosen from a manual search
		"""
		# Define filter function for determining intersection between signed
		# items and manually-searched items
		# This function checks that result item and signed item have same
		# clinicalItemId, listIndex (though s_item index will be ahead), and location source
		filter_fn_manual = lambda r_item, s_item: r_item['clinicalItemId'] == s_item['clinicalItemId'] and r_item['listIndex'] == s_item['listIndex'] - 1 and r_item['source'] == s_item['source']
		# For older versions of tracker data:
		filter_fn_manual_older = lambda r_item, s_item: r_item['clinicalItemId'] == s_item['clinicalItemId'] and r_item['storeTime'] == s_item['storeTime'] and r_item['source'] == s_item['source']
		# Define filter function for determining intersection between signed
		# items from manual search and recommomended
		# This function checks that result item and signed item have same
		# clinicalItemId and that the listIndex of recommended item is less
		# than or equal to that of the signed item. This ignores
		# results of the item that appeared after the item was already signed.
		filter_fn_recommended = lambda r_item, s_item: r_item['clinicalItemId'] == s_item['clinicalItemId'] and r_item['listIndex'] <= s_item['listIndex'] - 1
		# For older versions of tracker data:
		filter_fn_recommended_older = lambda r_item, s_item: r_item['clinicalItemId'] == s_item['clinicalItemId'] and r_item['storeTime'] <= s_item['storeTime']

		# First get the manually searched signed items
		manual_search_results = self.get_manually_searched_options()
		if self.version in ['v4', 'v5']:
			signed_from_manual = self._result_signed_intersection(manual_search_results, self.signed_orders_collection, filter_fn=filter_fn_manual)
		else:
			signed_from_manual = self._result_signed_intersection(manual_search_results, self.signed_orders_collection, filter_fn=filter_fn_manual_older)
		# Next get the manually searched items that also appeared previously
		# in recommended results
		recommended_results = self.get_recommended_options(include_related=include_related)
		if self.version in ['v4', 'v5']:
			missed_items = self._result_signed_intersection(recommended_results, signed_from_manual, filter_fn_recommended)
		else:
			missed_items = self._result_signed_intersection(recommended_results, signed_from_manual, filter_fn_recommended_older)
		return missed_items

	def get_unique(self, collection, key_fn):
		""""Return list of unique values, where the value of the objects in the
		collection is determined by the key function. Note that any order
		in the collection will not be preserved
		Args:
			collection (list): a list of objects to be filtered
			key_fn (fn): function that takes an object from collection and
				returns a value that will be used to consider uniqueness
		Returns:
			unique_vals (list): list of unique values extracted from collection
		"""
		values = list(map(key_fn, collection))
		unique_vals = list(set(values))
		return unique_vals

	def _clinical_item_id_key_fn(self, item):
		"""Returns clinical item value from item object"""
		return item['clinicalItemId']

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
	headers = ["user", "patient", "start_time", "elapsed_time", "total_num_clicks", "num_note_clicks", "num_results_review_clicks", "recommended_options", "unqique_recommended_options", "manual_search_options", "total_orders", "orders_from_recommender", "orders_from_manual_search", "orders_from_recommender_missed"]
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
			fields.append(siman.user)  # "user"
			fields.append(siman.patient)  # "patient"
			fields.append(siman.start_time)  # "start_time"
			fields.append(siman.elapsed_time())  # "elapsed_time"
			fields.append(siman.number_mouse_clicks_all())  # "total_num_clicks"
			# fields.append(siman.number_mouse_clicks(filters=['FindOrders']))  # "num_manual_searches"
			fields.append(siman.number_mouse_clicks(filters=['Notes']))  # "num_note_clicks"
			fields.append(siman.number_mouse_clicks(filters=['ResultsReview']))  # "num_results_review_clicks"
			fields.append(len(siman.get_recommended_options()))  # "recommended_options"
			fields.append(len(siman.get_unique(siman.get_recommended_options(), key_fn=siman._clinical_item_id_key_fn)))  # "unqique_recommended_options"
			fields.append(len(siman.get_manually_searched_options()))  # "manual_search_options"
			fields.append(len(siman.signed_orders_collection))  # "total_orders"
			fields.append(len(siman.get_signed_from_recommended()))  # "orders_from_recommender"
			fields.append(len(siman.get_signed_from_manual_search()))  # "orders_from_manual_search"
			fields.append(len(siman.get_signed_missed_recommended()))  # "orders_from_recommender_missed"
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
