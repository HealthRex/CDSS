import torch
import torch.nn.functional as F


class SimpleGRU(nn.Module):
    def __init__(self, vocab_size, embedding_size=512, hidden_size=256,
         num_layers=1):
        super(SimpleGRU).__init__()
        self.vocab_size = vocab_size
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.embedding_layer = torch.nn.Embedding(
            num_embeddings=self.vocab_size,
            embedding_dim=self.embedding_size
        )
        self.gru = torch.nn.GRU(
            input_size=self.embedding_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers
        )
        self.sigmoid = torch.nn.Sigmoid()

    def forward(self, x):
        embeddings = self.embedding_layer(x)
        output, h_n = self.gru(embeddings)
        y_hat = self.sigmoid(h_n)
        return x
