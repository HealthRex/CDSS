import numpy as np
import torch
from torch.nn.utils.rnn import pad_sequence 

# Needed to batch data with variable length inputs
def custom_collate(data): 
    inputs = [torch.tensor(d['sequence']) for d in data]
    labels = [torch.tensor(d['labels']) for d in data]
    time_deltas = [torch.tensor(d['time_deltas']) for d in data]
    inputs = pad_sequence(inputs, batch_first=True, padding_value=-1)
    labels = pad_sequence(labels, batch_first=True, padding_value=-1)
    labels = pad_sequence(time_deltas, batch_first=True, padding_value=-1)
    lengths = [len(d['sequnce']) for d in data]
    return {
        'sequence': inputs, 
        'label': labels,
        'time_deltas' : time_deltas,
        'lenghts' : lengths
    }

class SequenceDataset(torch.utils.data.Dataset):
    """
    Defines sequence dataset used for sequence models
    """

    def __init__(self, sequences, one_label_per_sequence=False):
        'Initialization'
        self.sequences = sequences
        self.one_label = one_label_per_sequence

    def __len__(self):
        'Denotes the total number of samples'
        return len(self.labels)

    def __getitem__(self, index):
        'Generates one sample of data'
        data = np.loadz(self.sequences[index])

        # Select sample
        sequence =  data['sequence']
        if self.one_label:
            labels = data['label'][0]
        else:
            labels = data['label']
        time_deltas = data['time_delta']
        return {'sequence' : sequence,
                'label' : labels,
                'time_deltas' : time_deltas}


