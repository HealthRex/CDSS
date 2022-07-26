from ipaddress import collapse_addresses
import os
import json
import sys
import argparse
from glob import glob
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy  as np
from sklearn.metrics import roc_auc_score
import pandas as pd
sys.path.insert(1, '../../medinfo/dataconversion/')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/conorcorbin/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'mining-clinical-decisions'
from datasets import SequenceDataset, custom_collate
from trainers import SequenceTrainer
from pytorch_models import PatientDayGRU

import pdb

parser = argparse.ArgumentParser(description='Pipeline to train CBC models')
parser.add_argument(
    '--datapath',
    default='./20220721_cbc_small_model_info/',
    help='where input data is saved'
)
parser.add_argument(
    '--run_name',
    default='run_0',
    help='name the training run'
)
parser.add_argument(
    '--learning_rate',
    default=1e-4,
    type=float,
    help='for adam opt'
)
parser.add_argument(
    '--weight_decay',
    default=1e-5,
    type=float,
    help='for adam opt'
)
parser.add_argument(
    '--dropout',
    default=0.2,
    type=float,
    help='regularization'
)
parser.add_argument(
    '--scheduler_gamma',
    default=0.1,
    type=float,
    help='learning rate scheduler'
)
parser.add_argument(
    '--scheduler_step_size',
    default=20,
    type=int,
    help='reduce learning rate every x epochs'
)
parser.add_argument(
    '--num_epochs',
    default=100,
    type=int,
    help='max number of epochs'
)
parser.add_argument(
    '--stopping_tolerance',
    default=20,
    type=int,
    help='exit if no improvement after x epochs'
)
parser.add_argument(
    '--stopping_metric',
    default='auc',
    help='metric to use for early stopping'
)
parser.add_argument(
    '--batch_size',
    default=32,
    help='batch size...'
)
parser.add_argument(
    '--num_targets',
    default=3,
    help='batch size...'
)
parser.add_argument(
    '--random_state',
    default=42,
    help='for randoms sake'
)
args = parser.parse_args()

# Outpath
outpath = os.path.join(args.datapath, 'runs', args.run_name)
os.makedirs(outpath, exist_ok=True)

# Dump a config file
with open(os.path.join(outpath, 'config.json'), 'w') as f:
    json.dump(args.__dict__, f)

# Load data
train_sequences = glob(os.path.join(args.datapath, 'train', '*.pt'))
val_sequences = glob(os.path.join(args.datapath, 'val', '*.pt'))
test_sequences = glob(os.path.join(args.datapath, 'test', '*.pt'))

# Instantiate datasets
train_dataset = SequenceDataset(train_sequences)
val_dataset = SequenceDataset(val_sequences)
test_dataset = SequenceDataset(test_sequences)

# Instantiate dataloaders
train_dataloader = DataLoader(
    train_dataset,
    batch_size=args.batch_size,
    num_workers=0,
    shuffle=True,
    collate_fn=custom_collate
)
val_dataloader = DataLoader(
    val_dataset,
    batch_size=args.batch_size,
    num_workers=0,
    shuffle=False,
    collate_fn=custom_collate
)
test_dataloader = DataLoader(
    test_dataset,
    batch_size=args.batch_size,
    num_workers=0,
    shuffle=False,
    collate_fn=custom_collate
)

# Multi-label loss
criterion = torch.nn.BCEWithLogitsLoss()

# Load vocab
with open(os.path.join(args.datapath, 'feature_vocab.npz'), 'r') as fp:
    vocab = json.load(fp)

# Model
model = PatientDayGRU(vocab_size=len(vocab))

# Optimizer
optimizer = torch.optim.Adam(
    model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

# Scheduler
scheduler = torch.optim.lr_scheduler.StepLR(
    optimizer, step_size=args.scheduler_step_size, gamma=args.scheduler_gamma)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Trainer
trainer = SequenceTrainer(
    outpath=outpath,
    model=model,
    criterion=criterion,
    optimizer=optimizer,
    device=device,
    train_dataloader=train_dataloader,
    val_dataloader=val_dataloader,
    test_dataloader=test_dataloader,
    stopping_metric=args.stopping_metric,
    stopping_tolerance=args.stopping_tolerance,
    num_epochs=args.num_epochs,
    scheduler=scheduler
)

# Train
trainer()

# Load best model, loop through test set and save predictions, labels
models = glob(os.path.join(outpath, "*.pt"))
models.sort(key=os.path.getmtime)
model = PatientDayGRU(vocab_size=len(vocab))
model.load_state_dict(torch.load(models[-1]))
model.to(device)
model.eval()

predictions, targets = [], []
for batch in tqdm(test_dataloader):
    model.zero_grad()
    sequence = batch['sequence'].to(device)
    seq_lengths = batch['lengths']
    labels = batch['labels'].to(device)
    time_deltas = batch['time_deltas'].to(device)
    output = model(sequence, seq_lengths, time_deltas)
    loss = criterion(output, labels.float())
    predictions.append(output.cpu().detach().numpy())
    targets.append(labels.cpu().detach().numpy())
predictions = np.concatenate(predictions)
targets = np.concatenate(targets)
auc = roc_auc_score(targets, predictions)
print(f"AUC on test: {auc}")
observation_ids = [a.split('/')[-1].split('.')[0] for a in test_sequences]
df = pd.DataFrame(data={
    'observation_ids' : observation_ids,
    'predictions' : predictions,
    'labels' : 'targets'
})

df.to_csv(os.path.join(outpath, 'scores_on_test.csv'))

torch.save(model.state_dict(),
    os.path.join(outpath, f'model_final.pt'))

