import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from transformers import AutoModelForCausalLM, AutoTokenizer

from helper_functions import (
    get_auth_keys
)

def run_inference(rank, world_size, model_name_or_path, prompts):
    
    print(f"\nInitialize the process group")
    torch.distributed.init_process_group(
        backend='nccl',
        init_method='env://',
        world_size=world_size,
        rank=rank
    )
    
    print(f"\nSet the device for the current rank")
    device = torch.device("cuda", rank)
    
    print(f"\nLoading authentication keys")
    auth_keys = get_auth_keys(
        auth_keys_path=auth_keys_path
    )

    print(f"\nLoad the model and move it to the specified device")
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_name_or_path, 
        token=auth_keys['HF_API_KEY'][0]
    )
    model.to(device)
    
    print(f"\nWrap the model with DistributedDataParallel")
    model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank])
    
    print(f"\nLoad the tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    
    print(f"\nGet the prompt for the current rank")
    prompt = prompts[rank % len(prompts)]
    
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
    output = model.generate(
        input_ids=input_ids,
        temperature=0.2,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
        max_new_tokens=4096
    )
    
    print(f"\nDecode and print the output for each rank")
    print(f"Output for rank {rank}:\n{tokenizer.decode(output[0])}\n")

def main():
    print("\nInitialize model and prompts")
    model_name_or_path = "m42-health/med42-70b"
    prompts = [
        "Our patient was evaluated for mitral regurgitation in 2013 and again in 2019 but there was nothing found.",
        "The patient was diagnosed with mitral regurgitation",
        "mitral regurgitation was considered on the differential, but it turned out to be atrial regurgitation"
    ]
    
    print(f"\nSet the world size to the number of GPUs you have")
    world_size = 1
    
    print(f"\nSpawn one process for each GPU:")
    mp.spawn(
        run_inference,
        args=(world_size, model_name_or_path, prompts),
        nprocs=world_size,
        join=True
    )

if __name__ == "__main__":
    main()
