#!/usr/bin/env python3
"""
Recommender System Experiment Runner

This script runs experiments with multiple recommendation models using RecBole framework.
It supports data preparation, model training, evaluation, and result comparison.
"""

import argparse
import os
import sys
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.model.general_recommender import BPR
from recbole.model.sequential_recommender import SASRec
from recbole.trainer import Trainer
from recbole.utils import init_seed, init_logger

from generate_synthetic_data import generate_synthetic_data


def ensure_data_exists(data_dir: str = 'data') -> None:
    """Generate synthetic data if it doesn't exist."""
    train_file = os.path.join(data_dir, 'train.csv')
    if not os.path.exists(train_file):
        print("Generating synthetic data...")
        generate_synthetic_data(data_dir)

def prepare_benchmark_files(data_dir: str = 'data', dataset_name: str = 'econsultant') -> Dict[str, Any]:
    """
    Convert CSV files to RecBole .inter format for benchmark loading.
    
    Args:
        data_dir: Directory containing train.csv, valid.csv, test.csv
        dataset_name: Name of the dataset
        
    Returns:
        Dictionary with dataset statistics
    """
    print("Preparing benchmark files for RecBole...")
    
    # Check that the CSV files exist
    train_file = os.path.join(data_dir, 'train.csv')
    valid_file = os.path.join(data_dir, 'valid.csv') 
    test_file = os.path.join(data_dir, 'test.csv')
    
    if not all(os.path.exists(f) for f in [train_file, valid_file, test_file]):
        raise FileNotFoundError(f"Missing data files in {data_dir}. Need train.csv, valid.csv, test.csv")
    
    # Read CSV files
    train_df = pd.read_csv(train_file)
    valid_df = pd.read_csv(valid_file)
    test_df = pd.read_csv(test_file)
    
    # Convert timestamps to Unix timestamps (float)
    for df in [train_df, valid_df, test_df]:
        df['timestamp'] = pd.to_datetime(df['timestamp']).astype('int64') / 1e9
    
    # Create .inter files that RecBole expects
    for split_name, df in [('train', train_df), ('valid', valid_df), ('test', test_df)]:
        inter_file = f'{dataset_name}.{split_name}.inter'
        with open(inter_file, 'w') as f:
            f.write("user_id:token\titem_id:token\ttimestamp:float\n")
            df[['user_id', 'item_id', 'timestamp']].to_csv(f, sep='\t', index=False, header=False)
    
    all_data = pd.concat([train_df, valid_df, test_df], ignore_index=True)
    
    stats = {
        'total_interactions': len(all_data),
        'unique_users': all_data['user_id'].nunique(),
        'unique_items': all_data['item_id'].nunique(),
        'train_interactions': len(train_df),
        'valid_interactions': len(valid_df), 
        'test_interactions': len(test_df)
    }
    
    print(f"Dataset prepared: {stats['total_interactions']:,} total interactions")
    print(f"- Train: {stats['train_interactions']:,}, Valid: {stats['valid_interactions']:,}, Test: {stats['test_interactions']:,}")
    print("✅ Using exact pre-defined splits")
    
    return stats


def get_model_class(model_name: str):
    """Get the model class based on model name."""
    model_classes = {
        'BPR': BPR,
        'SASRec': SASRec,
    }
    return model_classes.get(model_name)


def configure_model(model_name: str, dataset_name: str, 
                   config_files: List[str], data_path: str = '.') -> Config:
    """
    Configure model-specific settings.
    
    Args:
        model_name: Name of the model ('BPR', 'SASRec', etc.)
        dataset_name: Name of the dataset
        config_files: List of configuration files
        data_path: Path to data directory
        
    Returns:
        Configured Config object
    """
    config = Config(model=model_name, dataset=dataset_name, config_file_list=config_files)
    config['data_path'] = data_path
    
    # RecBole will use benchmark files directly - no need for manual eval_args
    
    # Model-specific configurations
    if model_name == 'BPR':
        config['loss_type'] = 'BPR'
        config['train_neg_sample_args'] = {
            'distribution': 'uniform', 
            'sample_num': 1, 
            'alpha': 1.0, 
            'dynamic': False, 
            'candidate_num': 0
        }
    elif model_name == 'SASRec':
        config['train_neg_sample_args'] = None
        config['loss_type'] = 'CE'
    
    return config



def print_experiment_results(results: Dict[str, Dict[str, float]], 
                           dataset_stats: Dict[str, Any]) -> None:
    """
    Print comprehensive experiment results.
    
    Args:
        results: Dictionary of model results
        dataset_stats: Dictionary containing dataset statistics
    """
    print(f"\n{'='*60}")
    print("FINAL EXPERIMENT RESULTS")
    print(f"{'='*60}")
    
    if not results:
        print("No models were successfully trained. Please check the configuration and data.")
        return
    
    # Print dataset statistics
    print(f"\nDataset Statistics:")
    print(f"- Total interactions: {dataset_stats['total_interactions']}")
    print(f"- Unique users: {dataset_stats['unique_users']}")
    print(f"- Unique items: {dataset_stats['unique_items']}")
    
    # Create comparison table
    print(f"\nModel Performance Comparison:")
    print("-" * 80)
    
    comparison_data = []
    for model_name, metrics in results.items():
        row = {'Model': model_name}
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                row[metric_name] = f"{value:.4f}"
        comparison_data.append(row)
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.to_string(index=False))
    
    # Find best performing model
    best_model = None
    best_score = -1
    
    for model_name, metrics in results.items():
        ndcg_10 = metrics.get('ndcg@10', metrics.get('NDCG@10', 0))
        if ndcg_10 > best_score:
            best_score = ndcg_10
            best_model = model_name
    
    if best_model:
        print(f"\n🏆 Best performing model: {best_model}")
        print(f"   Best NDCG@10 score: {best_score:.4f}")
        
        print(f"\nDetailed results for {best_model}:")
        for metric, value in results[best_model].items():
            print(f"  {metric}: {value:.4f}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run recommender system experiments with multiple models",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--models', 
        nargs='+', 
        default=['BPR', 'SASRec'],
        help='List of models to train'
    )
    
    parser.add_argument(
        '--dataset', 
        default='econsultant',
        help='Dataset name'
    )
    
    parser.add_argument(
        '--config-files', 
        nargs='+', 
        default=['configs/base.yaml'],
        help='List of configuration files'
    )
    
    parser.add_argument(
        '--data-dir', 
        default='data',
        help='Directory containing CSV data files'
    )
    
    parser.add_argument(
        '--data-path', 
        default='.',
        help='Path for RecBole data files'
    )
    
    return parser.parse_args()


def train_single_model(model_name: str, dataset_name: str, config_files: List[str],
                      data_path: str = '.') -> Optional[Dict[str, float]]:
    """
    Train a single model and return its test results.
    
    Args:
        model_name: Name of the model to train
        dataset_name: Name of the dataset
        config_files: List of configuration files
        data_path: Path to data directory
        
    Returns:
        Dictionary of test results or None if training failed
    """
    print(f"\n{'='*50}")
    print(f"Training model: {model_name}")
    print(f"{'='*50}")
    
    try:
        # Configure model
        config = configure_model(model_name, dataset_name, config_files, data_path)
        init_seed(config['seed'], config['reproducibility'])
        
        # Create dataset and prepare data
        dataset = create_dataset(config)
        train_data, valid_data, test_data = data_preparation(config, dataset)
        
        # Get model class
        model_class = get_model_class(model_name)
        if model_class is None:
            print(f"Unknown model: {model_name}")
            return None
        
        # Initialize model and trainer
        model = model_class(config, train_data.dataset).to(config['device'])
        trainer = Trainer(config, model)
        
        # Train the model
        print(f"Starting training for {model_name}...")
        best_valid_score, best_valid_result = trainer.fit(train_data, valid_data)
        print(f"Best validation score: {best_valid_score:.4f}")
        
        # Evaluate on test set
        print(f"Evaluating {model_name} on test set...")
        test_result = trainer.evaluate(test_data)
        
        print(f"Test results for {model_name}:")
        for metric, value in test_result.items():
            print(f"  {metric}: {value:.4f}")
            
        return test_result
        
    except Exception as e:
        print(f"Error training {model_name}: {str(e)}")
        print(f"Skipping {model_name}...")
        return None


def train_multiple_models(models: List[str], dataset_name: str, 
                         config_files: List[str], data_path: str = '.') -> Dict[str, Dict[str, float]]:
    """
    Train multiple models and return their results.
    
    Args:
        models: List of model names to train
        dataset_name: Name of the dataset
        config_files: List of configuration files
        data_path: Path to data directory
        
    Returns:
        Dictionary mapping model names to their test results
    """
    results = {}
    
    for model_name in models:
        result = train_single_model(model_name, dataset_name, config_files, data_path)
        if result is not None:
            results[model_name] = result
    
    return results


def main():
    """Main experiment function."""
    args = parse_arguments()
    
    print("Starting Recommender System Experiment")
    print(f"Models to test: {', '.join(args.models)}")
    print(f"Dataset: {args.dataset}")
    print(f"Config files: {', '.join(args.config_files)}")
    
    try:
        # Step 1: Ensure data exists
        ensure_data_exists(args.data_dir)
        
        # Step 2: Prepare benchmark .inter files (RecBole will load these directly)
        dataset_stats = prepare_benchmark_files(args.data_dir, args.dataset)
        
        # Step 3: Initialize logger (using first model's config)
        init_config = configure_model(args.models[0], args.dataset, args.config_files, args.data_path)
        init_logger(init_config)
        
        # Step 4: Train multiple models
        results = train_multiple_models(args.models, args.dataset, args.config_files, args.data_path)
        
        # Step 5: Print results
        print_experiment_results(results, dataset_stats)
        
    except Exception as e:
        print(f"Experiment failed: {str(e)}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("Experiment completed!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
