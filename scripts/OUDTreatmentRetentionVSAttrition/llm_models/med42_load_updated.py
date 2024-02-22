import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from helper_functions import get_auth_keys

def main(auth_keys_data):
    model_name_or_path = "m42-health/med42-70b"

    # Ensure CUDA is available
    if not torch.cuda.is_available():
        raise SystemError("CUDA is not available on this system.")

    # Use DataParallel to utilize multiple GPUs
    print(f"\nBuilding {model_name_or_path} Model")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name_or_path,
        token=auth_keys_data['HF_API_KEY'][0]
    )
    model = torch.nn.DataParallel(model)
    model.to(device)
    print(f"Build Successful")

    print(f"\nLoading {model_name_or_path} Tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=model_name_or_path,
        token=auth_keys_data['HF_API_KEY'][0]
    )
    print(f"Tokenizer Loaded")

    # Example prompt, replace with actual prompt as necessary
    prompt = "Example text that requires a label."

    print(f"\nGenerate the prompt template")
    prompt_template = f'''
    <|system|>: "You are a helpful medical assistant. Label the text with a 1 if the patient has mitral regurgitation or a 0 if the patient does not have mitral regurgitation. Here are some examples: 
    the patient was diagnosed with depression => 1 
    the effective forward lvef was mildly depressed at 54% => 0"
    <|prompter|>:{prompt}
    <|assistant|>:
    '''
    print(f"prompt_template: {prompt_template}")

    print(f"\nTokenize the input and move it to the correct device")
    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.to(device)
    
    print(f"\nGenerate the output")
    output = model.module.generate(
        input_ids=input_ids,
        temperature=0.2,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        max_new_tokens=4096
    )
    print(f"Output generated")

    # Convert output to text (if needed)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"Generated text: {generated_text}")

if __name__ == "__main__":
    auth_keys_data = get_auth_keys()
    main(auth_keys_data)
