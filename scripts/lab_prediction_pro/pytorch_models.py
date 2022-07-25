import torch
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence
from torch.nn.utils.rnn import pad_packed_sequence

import pdb

class PatientDayGRU(torch.nn.Module):
    def __init__(self, vocab_size, embedding_size=512, hidden_size=256,
         output_size=1, num_layers=1, dropout=0.2):
        super(PatientDayGRU, self).__init__()
        self.vocab_size = vocab_size+1
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size

        # Embed collection of tokens within patient days
        self.embedding_layer = torch.nn.EmbeddingBag(
            num_embeddings=self.vocab_size,
            embedding_dim=self.embedding_size-1, # because we're concating time
            padding_idx=0
        )

        # GRU
        self.gru = torch.nn.GRU(
            input_size=self.embedding_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers
        )

        # Classification
        self.classification_layer = torch.nn.Sequential(
            torch.nn.Linear(self.hidden_size, int(self.hidden_size/2)),
            torch.nn.Dropout(dropout),
            torch.nn.ReLU(),
            torch.nn.Linear(int(self.hidden_size/2), self.output_size),
        )

    def forward(self, x, x_lengths, time_deltas):
        # Embed all patient days and reshape
        x_stacked = torch.reshape(x, (x.shape[0]*x.shape[1], x.shape[2]))
        x_embed = self.embedding_layer(x_stacked)
        x_embed = torch.reshape(x_embed, 
                               (x.shape[0], x.shape[1], x_embed.shape[1]))
        time_deltas = torch.unsqueeze(time_deltas, dim=2)

        try:
            x_embed = torch.cat((x_embed, time_deltas), dim=2)
        except:
            pdb.set_trace()

        # Pack padded days for input to GRU
        packed_embeddings = pack_padded_sequence(x_embed,
                                                 x_lengths,
                                                 batch_first=True,
                                                 enforce_sorted=False)
        output_packed, hidden = self.gru(packed_embeddings)

        output_padded, output_lengths = pad_packed_sequence(
            output_packed, batch_first=True)
        
        hidden = torch.squeeze(hidden, dim=0)
        yhat = self.classification_layer(hidden)
        return torch.squeeze(yhat, dim=1)
