# Large Language Model Assertion Pipeline (updated - 2/25/24)
## For question, contact: Ivan Lopez (ivlopez@stanford.edu or slack)

This code is for the large language model assertion pipeline. Detailed instructions coming soon!

### Pipeline flow:
1. Run ```CDSS/scripts/llm_assertion/run_umls_synonym_ner.py``` and ```CDSS/scripts/llm_assertion/run_dataset_ner.py``` to build NER datasets (recommend using targeted NER prompts instead of broad NER prompts for NER dataset pull)
2. (Optional - highly recommended) Run ```CDSS/scripts/llm_assertion/run_ner_cosine_similarity.py``` followed by ```CDSS/scripts/llm_assertion/run_llm_filter_cosine_sim_ner_output.py``` to filter NER outputs (recommend using SecureGPT to filter NER outputs to remove the low-yield named entities --> also helpful to review filtered NER outputs and remove those that are not related to your target entity)
3. Run ```CDSS/scripts/llm_assertion/run_extraction.py``` to build target-matcher and extract high-yield text from clinical notes
4. Run ```CDSS/scripts/llm_assertion/run_llm_assertion.py``` to generate LLM assertions

### To-do:
1. Build and start-to-end pipeline (current code is segmented)
2. Write-up proper documentation for code and functions
3. Create a proper tutorial (including how to set-up VM, how to download models into PHI-safe env, how to properly run pipeline, prompt engineering, etc)
4. Clean and push prompt generation code
