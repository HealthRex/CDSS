from transformers import AutoModelForCausalLM, AutoModel, AutoTokenizer

from helper_functions import (
    get_auth_keys
)

def main(
        auth_keys_data,
        model_name_or_path: str = "m42-health/med42-70b",
):

    print(f"\nBuilding {model_name_or_path} Model")
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name_or_path, 
        device_map="auto", 
        token=auth_keys_data['HF_API_KEY'][0]
    )
    print(f"Build Successful")

    print(f"\nLoading {model_name_or_path} Tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=model_name_or_path,
        token=auth_keys_data['HF_API_KEY'][0]
    )
    print(f"Tokenizer Loaded")

if __name__ == "__main__":
    main()