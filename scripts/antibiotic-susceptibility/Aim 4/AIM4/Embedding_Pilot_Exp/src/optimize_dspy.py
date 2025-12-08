import dspy
import asyncio
import os
import logging
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from llm.dspy_adapter import HealthRexDSPyLM
from util.DSPy_modules_dspy import ErrorIdentifierModule, IdentifyErrorSignature
from data.loader_dspy import load_data  # Assuming this loads your data

# 1. Setup DSPy
model_name = "gpt-5"  # Use a cheaper model for optimization if possible, or your main model
lm = HealthRexDSPyLM(model_name=model_name)
dspy.settings.configure(lm=lm)

# 2. Define Metric
# The metric checks if the predicted error presence matches the ground truth
def validate_error_identifier(example, pred, trace=None):
    # Strict match on error presence
    if example.assessment.error_present != pred.assessment.error_present:
        return False
    
    # If error is present, check if summaries are somewhat similar (optional/advanced)
    # For now, we stick to binary classification accuracy as the primary signal
    return True

async def main():
    # 3. Load Data
    # We need a set of examples with "Gold Standard" answers.
    # Here we assume load_data returns a DataFrame, and we convert it to DSPy Examples.
    # You need a dataset where you KNOW the correct answer (e.g. human labeled).
    
    # For demonstration, let's assume we have a list of raw examples
    # In reality, you should load your "Golden Dataset" here.
    # train_data = [dspy.Example(patient_message="...", llm_response="...", assessment=ErrorIdentifierOutput(...)).with_inputs("patient_message", "llm_response")]
    
    print("Loading data for optimization...")
    # raw_data = load_data(size=50) # Load 50 examples
    
    # Convert to DSPy Examples (Pseudo-code, adjust to your actual data structure)
    # trainset = []
    # for _, row in raw_data.iterrows():
    #     # Construct the expected output object
    #     expected_output = ErrorIdentifierOutput(...) 
    #     ex = dspy.Example(
    #         patient_message=row['Patient Message'],
    #         llm_response=row['Suggested Response from LLM'],
    #         # ... other inputs
    #         assessment=expected_output
    #     ).with_inputs('patient_message', 'llm_response', 'patient_info', 'clinical_notes', 'previous_messages', 'retrieved_pairs')
    #     trainset.append(ex)

    # For now, we will create a dummy training set to show the syntax
    trainset = [
        dspy.Example(
            patient_message="My chest hurts",
            llm_response="Take an aspirin",
            patient_info="Age 65, Hypertensive",
            clinical_notes="History of MI",
            previous_messages="",
            retrieved_pairs="",
            # This assessment is what we expect the model to produce
            assessment=dspy.Prediction(
                error_present=True, 
                error_summary="Missed triage of chest pain.", 
                error_highlights=[] # simplified
            ) 
        ).with_inputs("patient_message", "llm_response", "patient_info", "clinical_notes", "previous_messages", "retrieved_pairs")
    ]

    # 4. compile (Optimize)
    print("Starting optimization...")
    
    # BootstrapFewShotWithRandomSearch:
    # - Generates variations of the instructions
    # - Selects best few-shot examples from your trainset
    optimizer = BootstrapFewShotWithRandomSearch(
        metric=validate_error_identifier,
        max_bootstrapped_demos=2,
        max_labeled_demos=2,
        num_candidate_programs=5,
        num_threads=1  # Set to 1 because our LM adapter is effectively sync/blocking
    )

    # The student is our module
    student = ErrorIdentifierModule()
    
    # Run optimization
    optimized_program = optimizer.compile(student, trainset=trainset)
    
    # 5. Save
    save_path = "optimized_identifier.json"
    optimized_program.save(save_path)
    print(f"Optimized program saved to {save_path}")
    
    # Usage in production:
    # loaded_program = ErrorIdentifierModule()
    # loaded_program.load(save_path)

if __name__ == "__main__":
    # Since our adapter uses asyncio internally, we run the main script
    # But the optimizer itself calls the LM synchronously. 
    # Our adapter handles the loop creation/nesting.
    asyncio.run(main())

