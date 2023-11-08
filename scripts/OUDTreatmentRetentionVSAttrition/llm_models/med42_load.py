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
    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    
    print(f"\nGenerate the output")
    output = model.generate(
        input_ids=input_ids,
        temperature=0.2,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        max_new_tokens=4096
    )

if __name__ == "__main__":
    main()