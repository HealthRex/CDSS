import numpy as np
import torch
from torch.nn.utils.rnn import pad_sequence 

import pdb

# Needed to batch data with variable length inputs
def custom_collate(data): 
    """
    Data has sequences that are all variable length. Number of sequences
    is variable per batch, and sequence length is variable across batches.

    Want sequence to have shape (B, N_max, S_max) where B is batch size
    N_max is max number of days in each batch, S_max is max number of tokens
    within a day for each batch 
    """
    inputs = [torch.tensor(d['sequence']) for d in data]
    labels = [torch.tensor(d['labels']) for d in data]
    time_deltas = [torch.tensor(d['time_deltas']) for d in data]
    pdb.set_trace()
    inputs = pad_sequence(inputs, batch_first=True)
    pdb.set_trace()
    labels = pad_sequence(labels, batch_first=True, padding_value=-1)
    labels = pad_sequence(time_deltas, batch_first=True, padding_value=-1)
    lengths = [len(d['sequnce']) for d in data]
    return {
        'sequence': inputs, 
        'labels': labels,
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
        return len(self.sequences)

    def __getitem__(self, index):
        'Generates one sample of data'
        data = torch.load(self.sequences[index])

        # Select sample
        sequence =  data['sequence']
        if self.one_label:
            labels = data['labels'][0]
        else:
            labels = data['labels']
        time_deltas = data['time_deltas']
        return {'sequence' : sequence,
                'labels' : labels,
                'time_deltas' : time_deltas}


