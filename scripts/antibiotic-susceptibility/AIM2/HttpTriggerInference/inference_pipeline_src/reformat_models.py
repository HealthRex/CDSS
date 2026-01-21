"""
Script to reformat XGBoost models into the expected structure for AntibioticModelInference.

This script combines:
- The trained XGBoost model from {antibiotic}_xgb.json
- The feature list and metadata from {antibiotic}_metadata.pkl

Into a single properly formatted .pkl file:
{
    'model': XGBClassifier object,
    'expected_features': [...],
    'metadata': {...}
}

Usage:
    python reformat_models.py                    # Process all antibiotics
    python reformat_models.py Ciprofloxacin     # Process specific antibiotic
"""

import os
import sys
import pickle
import joblib
from pathlib import Path
from typing import Optional


def reformat_model(
    antibiotic: str,
    models_dir: str = ".",
    output_dir: Optional[str] = None,
) -> bool:
    """
    Reformat a single antibiotic model into the expected structure.
    
    Args:
        antibiotic: Name of the antibiotic (e.g., 'Ciprofloxacin')
        models_dir: Directory containing the source files
        output_dir: Directory for output files (defaults to models_dir)
        
    Returns:
        True if successful, False otherwise
    """
    # Import xgboost here to provide better error message
    try:
        import xgboost as xgb
    except ImportError:
        print("ERROR: xgboost not installed. Run: pip install xgboost")
        return False
    except Exception as e:
        if "libomp" in str(e).lower() or "openmp" in str(e).lower():
            print("ERROR: OpenMP runtime not installed.")
            print("  Mac users: Run 'brew install libomp'")
            print("  Then try again.")
            return False
        raise
    
    models_dir = Path(models_dir)
    output_dir = Path(output_dir) if output_dir else models_dir
    
    # Find source files (handle case variations)
    json_path = None
    metadata_path = None
    
    for f in models_dir.iterdir():
        fname_lower = f.name.lower()
        abx_lower = antibiotic.lower().replace(" ", "_")
        
        if abx_lower in fname_lower and f.suffix == '.json':
            json_path = f
        elif abx_lower in fname_lower and 'metadata' in fname_lower and f.suffix == '.pkl':
            metadata_path = f
    
    if not json_path:
        print(f"ERROR: No .json model file found for '{antibiotic}'")
        print(f"  Expected: {antibiotic}_xgb.json or similar")
        return False
    
    if not metadata_path:
        print(f"ERROR: No metadata.pkl file found for '{antibiotic}'")
        print(f"  Expected: {antibiotic}_metadata.pkl or similar")
        return False
    
    print(f"Processing {antibiotic}...")
    print(f"  JSON model: {json_path.name}")
    print(f"  Metadata:   {metadata_path.name}")
    
    # Load the XGBoost model
    model = xgb.XGBClassifier()
    model.load_model(str(json_path))
    
    # Load metadata
    metadata_dict = joblib.load(metadata_path)
    
    # Extract what we need
    selected_features = metadata_dict.get('selected_features', [])
    best_tune = metadata_dict.get('best_tune', {})
    auc = metadata_dict.get('auc')
    
    # Verify feature count matches
    booster = model.get_booster()
    model_num_features = booster.num_features()
    
    if len(selected_features) != model_num_features:
        print(f"  WARNING: Feature count mismatch!")
        print(f"    Model expects {model_num_features} features")
        print(f"    Metadata has {len(selected_features)} features")
    
    # Create the reformatted structure
    reformatted = {
        'model': model,
        'expected_features': selected_features,
        'metadata': {
            'antibiotic': antibiotic,
            'auc': float(auc) if auc is not None else None,
            'best_tune': best_tune,
            'num_features': len(selected_features),
            'source_json': json_path.name,
            'source_metadata': metadata_path.name,
        }
    }
    
    # Save reformatted model
    # Use lowercase with underscores for consistency
    output_name = antibiotic.lower().replace(" ", "_").replace("-", "_") + ".pkl"
    output_path = output_dir / output_name
    
    with open(output_path, 'wb') as f:
        pickle.dump(reformatted, f)
    
    output_size_kb = output_path.stat().st_size / 1024
    print(f"  Saved: {output_name} ({output_size_kb:.1f} KB)")
    print(f"  Features: {len(selected_features)}")
    print(f"  AUC: {auc:.4f}" if auc else "  AUC: N/A")
    print()
    
    return True


def find_antibiotics(models_dir: str = ".") -> list:
    """Find all antibiotics that have both .json and _metadata.pkl files."""
    models_dir = Path(models_dir)
    
    # Find all metadata files
    metadata_files = [f for f in models_dir.iterdir() 
                     if 'metadata' in f.name.lower() and f.suffix == '.pkl']
    
    antibiotics = []
    for mf in metadata_files:
        # Extract antibiotic name from filename
        name = mf.name.replace('_metadata.pkl', '').replace('_metadata', '')
        antibiotics.append(name)
    
    return antibiotics


def main():
    # Get script directory
    script_dir = Path(__file__).parent
    models_dir = script_dir / "models"
    
    if not models_dir.exists():
        print(f"ERROR: Models directory not found: {models_dir}")
        return 1
    
    # Check for specific antibiotic argument
    if len(sys.argv) > 1:
        antibiotic = sys.argv[1]
        success = reformat_model(antibiotic, models_dir)
        return 0 if success else 1
    
    # Process all antibiotics
    antibiotics = find_antibiotics(models_dir)
    
    if not antibiotics:
        print("No antibiotics found with both .json and _metadata.pkl files")
        print(f"Looking in: {models_dir}")
        return 1
    
    print(f"Found {len(antibiotics)} antibiotics to process:")
    for abx in antibiotics:
        print(f"  - {abx}")
    print()
    
    success_count = 0
    for antibiotic in antibiotics:
        if reformat_model(antibiotic, models_dir):
            success_count += 1
    
    print(f"Completed: {success_count}/{len(antibiotics)} models reformatted")
    
    if success_count < len(antibiotics):
        print("\nMissing .json files? Copy them to the models directory:")
        print(f"  {models_dir}/")
        
    return 0 if success_count == len(antibiotics) else 1


if __name__ == "__main__":
    sys.exit(main())
