# Recommender System Evaluation Framework

A machine learning evaluation framework for recommender systems built using the [RecBole](https://github.com/RUCAIBox/RecBole) framework. This toolkit provides everything needed to evaluate recommendation algorithms on your data.

## 🚀 Features

- **Multiple Recommendation Models**: Supports BPR, SASRec and other RecBole-compatible models
- **Temporal Data Splitting**: train/validation/test splitting based on temporal patterns
- **Synthetic Data Generation**: Built-in synthetic data generator for testing and development
- **Comprehensive Evaluation**: Multiple metrics including Recall, Precision, and NDCG

## 📁 Core Files

```
├── configs/
│   └── base.yaml              # Model configuration and hyperparameters
├── run_experiment.py          # Main experiment runner
├── data_split.py             # E-consultant data preprocessing and temporal splitting
└── generate_synthetic_data.py # Synthetic data generator for testing
```

## 🛠 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Recommender
   ```

2. **Install dependencies**
   ```bash
   pip install recbole pandas numpy
   ```

## 🚀 Quick Start

### 1. Generate Synthetic Data (Optional)

```bash
# Generate synthetic data for testing
python generate_synthetic_data.py
```

### 2. Prepare Your Data

```bash
# Split your data into train/validation/test sets with temporal splitting
python data_split.py
```

### 3. Run Experiments

```bash
# Run with default models (BPR and SASRec)
python run_experiment.py

# Run with specific models
python run_experiment.py --models BPR SASRec

# Customize dataset and configuration
python run_experiment.py --dataset econsultant --config-files configs/base.yaml
```

## 📊 Data Format

### Input CSV Files
The system expects `train.csv`, `valid.csv`, `test.csv` with columns:
- `user_id`: Unique identifier for users
- `item_id`: Unique identifier for items  
- `timestamp`: Interaction timestamp

### Generated Files
The experiment runner automatically creates RecBole .inter format files:
- `econsultant.train.inter`
- `econsultant.valid.inter` 
- `econsultant.test.inter`

## ⚙️ Configuration

Model configurations are defined in `configs/base.yaml`:

```yaml
# Training parameters
epochs: 10
train_batch_size: 256
learning_rate: 0.001

# Evaluation metrics
topk: [5, 10]
metrics: ['Recall', 'Precision', 'NDCG']
valid_metric: 'NDCG@10'

# Model-specific parameters
max_seq_length: 50
hidden_size: 64
```

## 🤖 Supported Models

- **BPR (Bayesian Personalized Ranking)**: Matrix factorization with pairwise ranking
- **SASRec (Self-Attentive Sequential Recommendation)**: Sequential model with self-attention
- Easily extensible to other RecBole models

## 📈 Evaluation Metrics

- **Recall@K**: Proportion of relevant items retrieved
- **Precision@K**: Proportion of retrieved items that are relevant
- **NDCG@K**: Normalized Discounted Cumulative Gain

