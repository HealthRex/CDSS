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
    inputs = [d['sequence'] for d in data]
    labels = [torch.tensor(d['labels']) for d in data]
    patient_lens = [i.shape[0] for i in inputs]
    inputs_unwound = [inp[i] for inp in inputs for i in range(len(inp))]
    inputs_unwound_padded = pad_sequence(inputs_unwound, batch_first=True)
    inputs_padded = torch.split(inputs_unwound_padded, patient_lens)
    inputs_padded = pad_sequence(inputs_padded, batch_first=True)
    time_deltas = [torch.exp(torch.tensor(d['time_deltas'])*-1) for d in data]
    time_deltas = pad_sequence(time_deltas, batch_first=True)
    return {
        'sequence': inputs_padded, 
        'labels': torch.tensor([lab[0][0] for lab in labels]), # refactor 
        'time_deltas' : time_deltas,
        'lengths' : patient_lens
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


