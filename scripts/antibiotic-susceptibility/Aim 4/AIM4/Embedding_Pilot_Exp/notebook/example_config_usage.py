#!/usr/bin/env python3
"""
Example script showing how to use config.py with the automated error checking system.

This demonstrates different ways to use the configuration system.
"""

from automated_error_checking import AutomatedErrorChecker
import config

def example_1_basic_usage():
    """Example 1: Use all default config values"""
    print("=== Example 1: Basic Usage (All Defaults) ===")
    
    try:
        # This uses all values from config.py automatically
        processor = AutomatedErrorChecker()
        print(f"Using Excel file: {processor.excel_path}")
        print(f"Output directory: {processor.output_dir}")
        print(f"Model: {config.MODEL}")
        print(f"Delay: {config.DELAY_BETWEEN_CALLS}s")
        print("✅ Successfully initialized AutomatedErrorChecker")
    except ValueError as e:
        if "HEALTHREX_API_KEY" in str(e):
            print("⚠️  API Key not set - this is expected for demonstration")
            print("   To run actual processing, create a .env file with:")
            print("   HEALTHREX_API_KEY=your_api_key_here")
            print("   Install python-dotenv if not already installed: pip install python-dotenv")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    print()

def example_2_override_some_config():
    """Example 2: Override some config values"""
    print("=== Example 2: Override Some Config Values ===")
    
    try:
        # Override some values while keeping others from config
        processor = AutomatedErrorChecker(
            excel_path="../data/sampled_df_with_generated_questions.xlsx",
            output_dir="../custom_outputs"
        )
        
        print(f"✅ Successfully created processor with custom paths")
        print(f"   Excel: {processor.excel_path}")
        print(f"   Output: {processor.output_dir}")
        
        # Note: We don't actually call process_all_data here to avoid API calls
        print("   (Skipping actual processing to avoid API calls)")
        
    except ValueError as e:
        if "HEALTHREX_API_KEY" in str(e):
            print("⚠️  API Key not set - this is expected for demonstration")
            print("   To run actual processing, create a .env file with:")
            print("   HEALTHREX_API_KEY=your_api_key_here")
            print("   Install python-dotenv if not already installed: pip install python-dotenv")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    print()

def example_3_modify_config_programmatically():
    """Example 3: Modify config values programmatically"""
    print("=== Example 3: Modify Config Programmatically ===")
    
    try:
        # Temporarily modify config values
        original_model = config.MODEL
        original_delay = config.DELAY_BETWEEN_CALLS
        
        # Change config for this run
        config.MODEL = "gemini-2.5-pro"
        config.DELAY_BETWEEN_CALLS = 0.5
        
        processor = AutomatedErrorChecker()
        print(f"✅ Successfully created processor with modified config")
        print(f"   Model: {config.MODEL}")
        print(f"   Delay: {config.DELAY_BETWEEN_CALLS}s")
        
        # Restore original values
        config.MODEL = original_model
        config.DELAY_BETWEEN_CALLS = original_delay
        
    except ValueError as e:
        if "HEALTHREX_API_KEY" in str(e):
            print("⚠️  API Key not set - this is expected for demonstration")
            print("   To run actual processing, create a .env file with:")
            print("   HEALTHREX_API_KEY=your_api_key_here")
            print("   Install python-dotenv if not already installed: pip install python-dotenv")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    print()

def example_4_selective_saving():
    """Example 4: Use selective saving options"""
    print("=== Example 4: Selective Saving ===")
    
    try:
        # Temporarily disable some saving options
        original_save_inputs = config.SAVE_INPUTS
        original_save_parser = config.SAVE_PARSER_OUTPUTS
        
        config.SAVE_INPUTS = False  # Don't save input files
        config.SAVE_PARSER_OUTPUTS = False  # Don't save parser outputs
        
        processor = AutomatedErrorChecker()
        print(f"✅ Successfully created processor with selective saving")
        print(f"   Save inputs: {config.SAVE_INPUTS}")
        print(f"   Save parser outputs: {config.SAVE_PARSER_OUTPUTS}")
        print(f"   Save evaluator outputs: {config.SAVE_EVALUATOR_OUTPUTS}")
        print(f"   Save summary: {config.SAVE_SUMMARY}")
        
        # Restore original values
        config.SAVE_INPUTS = original_save_inputs
        config.SAVE_PARSER_OUTPUTS = original_save_parser
        
    except ValueError as e:
        if "HEALTHREX_API_KEY" in str(e):
            print("⚠️  API Key not set - this is expected for demonstration")
            print("   To run actual processing, create a .env file with:")
            print("   HEALTHREX_API_KEY=your_api_key_here")
            print("   Install python-dotenv if not already installed: pip install python-dotenv")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    print()

def example_5_batch_processing():
    """Example 5: Batch processing with different configs"""
    print("=== Example 5: Batch Processing ===")
    
    try:
        # Process in batches with different settings
        batches = [
            {"start": 0, "end": 10, "model": "gpt-4.1", "delay": 1.0},
            {"start": 10, "end": 20, "model": "gemini-2.5-pro", "delay": 0.5},
        ]
        
        for i, batch in enumerate(batches):
            print(f"Processing batch {i+1}: rows {batch['start']}-{batch['end']}")
            
            # Temporarily set config for this batch
            original_model = config.MODEL
            original_delay = config.DELAY_BETWEEN_CALLS
            
            config.MODEL = batch["model"]
            config.DELAY_BETWEEN_CALLS = batch["delay"]
            
            processor = AutomatedErrorChecker()
            print(f"   ✅ Created processor for batch {i+1}")
            print(f"   Model: {config.MODEL}, Delay: {config.DELAY_BETWEEN_CALLS}s")
            
            # Note: We don't actually call process_all_data here to avoid API calls
            print(f"   (Skipping actual processing to avoid API calls)")
            
            # Restore original config
            config.MODEL = original_model
            config.DELAY_BETWEEN_CALLS = original_delay
            
    except ValueError as e:
        if "HEALTHREX_API_KEY" in str(e):
            print("⚠️  API Key not set - this is expected for demonstration")
            print("   To run actual processing, create a .env file with:")
            print("   HEALTHREX_API_KEY=your_api_key_here")
            print("   Install python-dotenv if not already installed: pip install python-dotenv")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    print()

def show_current_config():
    """Show current configuration values"""
    print("=== Current Configuration ===")
    print(f"Excel Path: {config.EXCEL_PATH}")
    print(f"Output Directory: {config.OUTPUT_DIR}")
    print(f"Start Row: {config.START_ROW}")
    print(f"End Row: {config.END_ROW}")
    print(f"Model: {config.MODEL}")
    print(f"Delay Between Calls: {config.DELAY_BETWEEN_CALLS}s")
    print(f"Log Level: {config.LOG_LEVEL}")
    print(f"Save Inputs: {config.SAVE_INPUTS}")
    print(f"Save Parser Outputs: {config.SAVE_PARSER_OUTPUTS}")
    print(f"Save Evaluator Outputs: {config.SAVE_EVALUATOR_OUTPUTS}")
    print(f"Save Summary: {config.SAVE_SUMMARY}")
    print(f"Create Analysis DF: {config.CREATE_ANALYSIS_DF}")
    print()

if __name__ == "__main__":
    print("Config.py Usage Examples")
    print("=" * 50)
    
    # Show current config
    show_current_config()
    
    # Run all examples (they now handle missing API key gracefully)
    example_1_basic_usage()
    # example_2_override_some_config()
    # example_3_modify_config_programmatically()
    # example_4_selective_saving()
    # example_5_batch_processing()
    
    print("Examples completed successfully!")
    print("\n📝 Note: To run actual processing with API calls:")
    print("   1. Create a .env file with: HEALTHREX_API_KEY=your_api_key_here")
    print("   2. Install python-dotenv if not already installed: pip install python-dotenv")
    print("   3. Then run: python automated_error_checking.py") 