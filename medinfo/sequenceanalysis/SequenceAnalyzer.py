import types
from collections import defaultdict, deque

class SequenceAnalyzer(object):
  def __init__(self):
    self.built = False
    self.pipeline = []

  #TODO: do something cool where each function's input variables can change / are fluid
  def split_data(self, split_fn):
    assert len(self.pipeline) == 0
    def func(data):
      '''
      def splitByPatient(results):
        currentSplit = [results.next()]
        for result in results:
          if result[0] != currentSplit[-1][0]:
            yield currentSplit
            currentSplit = []
          currentSplit.append(result)
        yield currentSplit
      '''
      if isinstance(data, types.GeneratorType):
        current_split = [data.next()]
      elif isinstance(data, types.ListType):
        current_split = [data[0]]
        data = data[1:]
      for row in data:
        if split_fn(current_split, row):
          yield current_split
          current_split = []
        current_split.append(row)
      yield current_split
    self.pipeline.append(('split_data', func))

  def initialize_vars(self, vars_dict):
    self.vars = vars_dict

  def filter_row(self, filter_row_fn):
    pass

  def handle_sentinel_queue(self, handle_sentinel_queue_fn):
    def func(window_size, queue, vars_dict, row):
      if queue and queue[0][0] is None:
          handle_sentinel_queue_fn(window_size, queue, vars_dict, row)
          queue.clear()
    self.pipeline.append(('handle_sentinl_queue', func))

  # def filter_queue(self, filter_queue_fn, filter_if_fn=None, filter_else_handler_fn=None, filter_sentinel_fn=None):
  #   def func(window_size, queue, vars_dict, popped_queue, row):
  #     if queue:
  #       # TODO: handle NONE
  #       if filter_if_fn(window_size, queue, vars_dict, row):
  #         while queue and filter_queue_fn(window_size, queue, vars_dict, row):
  #           popped_queue = True
  #           queue.popleft()
  #       elif filter_else_handler_fn is not None:
  #         filter_else_handler_fn(window_size, queue, vars_dict, row)

  #     if filter_sentinel_fn is not None and popped_queue and len(queue) == 0:
  #       filter_sentinel_fn(window_size, vars_dict, row)
  #   self.pipeline.append('filter_queue', func)


  def filter_queue(self, filter_queue_fn, emptied_queue_handler_fn=None):
    def func(window_size, queue, vars_dict, row):
      popped_queue = False
      if queue and queue[0][0] is not None:
        while queue and filter_queue_fn(window_size, queue, vars_dict, row):
          popped_queue = True
          queue.popleft()
      if emptied_queue_handler_fn is not None and popped_queue and not queue:
        emptied_queue_handler_fn(window_size, vars_dict, row)
    self.pipeline.append('filter_queue', func)

  def set_var(self, var_name, set_value_fn):
    def func(window_size, queue, vars_dict, row):
      vars_dict[var_name] = set_value_fn(window_size, queue, vars_dict, row)
    self.pipeline.append(('set_var', func))

  def filter_sentinel(self, filter_sentinel_fn, use_vars):
    pass

  def add_row(self):
    pass

  def select_window(self, select_window_fn, use_vars):
    pass

  def compute_stats(self, compute_stats_fn, use_vars):
    pass

  def clear_queue(self, clear_window_fn, use_vars):
    pass

  def build(self):
    self.built = True

  def run(self, data, bins):
    # check if built
    assert self.built
    data_split_generator = data
    if self.pipeline[0][0] == 'split_data':
      data_split_generator = self.pipeline[0][1](data)
      self.pipeline = self.pipeline[1:]

    bins_queue = [deque() for _ in xrange(len(bins))]
    # key: (days back, consecutive), value: (total, next_normal)
    # stats = defaultdict(lambda: np.array([0, 0]))
    bins_vars_dict = [dict(self.vars) for _ in xrange(len(bins))]
    for data_split in data_split_generator:
      # print(data_split)
      for row in data_split:
        # print(row)
        for window_size, queue, vars_dict in zip(bins, bins_queue, bins_vars_dict):
          popped_queue = False
          for name, func in self.pipeline:
            if name == 'handle_sentinel_queue':
              popped_queue = func(window_size, queue, vars_dict, row)
            if name == 'filter_queue':
              popped_queue = func(window_size, queue, vars_dict, popped_queue, row)
    # pass
