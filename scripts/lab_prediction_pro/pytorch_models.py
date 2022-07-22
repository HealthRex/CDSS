import torch
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence
from torch.nn.utils.rnn import pad_packed_sequence

import pdb

class SimpleGRU(torch.nn.Module):
    def __init__(self, vocab_size, embedding_size=512, hidden_size=256,
         output_size=1, num_layers=1, dropout=0.2):
        super(SimpleGRU, self).__init__()
        self.vocab_size = vocab_size
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size

        # Embed
        self.embedding_layer = torch.nn.Embedding(
            num_embeddings=self.vocab_size,
            embedding_dim=self.embedding_size
        )

        # GRU
        self.gru = torch.nn.GRU(
            input_size=self.embedding_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers
        )

        # Classification
        self.classification_layer = torch.nn.Sequential(
            torch.nn.Linear(self.embedding_size, self.hidden_size),
            torch.nn.Dropout(dropout),
            torch.nn.ReLU(),
            torch.nn.Linear(self.hidden_size, self.output_size),
        )

    def forward(self, x, x_lengths):
        embeddings = self.embedding_layer(x)
        packed_embeddings = pack_padded_sequence(embeddings,
                                                 x_lengths,
                                                 batch_first=True,
                                                 enforce_sorted=False)
        output_packed, hidden = self.gru(packed_embeddings)
        output_padded, output_lengths = pad_packed_sequence(
            output_packed, batch_first=True)
        
        pdb.set_trace()
        yhat = self.classification_layer(output_padded)
        return output_padded
