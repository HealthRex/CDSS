import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from transformers import AutoModelForCausalLM, AutoTokenizer

from helper_functions import (
    get_auth_keys
)

def run_inference(rank, world_size, model_name_or_path, prompts, return_dict):
    try:
        dist.init_process_group(
            backend='nccl',
            init_method='env://',
            world_size=world_size,
            rank=rank
        )

        device = torch.device("cuda", rank)
        
        auth_keys = get_auth_keys()
        
        model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_name_or_path, 
            token=auth_keys['HF_API_KEY'][0]
        ).to(device)
        
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[rank])
        
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        
        # Determine the prompts for this rank, handling uneven distribution
        prompts_for_rank = prompts[rank::world_size]

        results = []

        for prompt in prompts_for_rank:
            prompt_template = f'''
            You are a helpful medical assistant. Label the text with a 1 if the patient has mitral regurgitation or a 0 if the patient does not have mitral regurgitation. Here are some examples: 
            the patient was diagnosed with depression => 1 
            the effective forward lvef was mildly depressed at 54% => 0
            {prompt}
            '''
            
            input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.to(device)
            
            output = model.generate(
                input_ids=input_ids,
                temperature=0.2,
                do_sample=True,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                max_new_tokens=4096
            )
            generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
            results.append((prompt, generated_text))

        return_dict[rank] = results
    except Exception as e:
        print(f"An error occurred on GPU {rank}: {e}")
        return_dict[rank] = None
    finally:
        dist.destroy_process_group()

def main():
    model_name_or_path = "m42-health/med42-70b"
    prompts = [
        # Assume there's a sufficient number of prompts to distribute across GPUs
    ]
    
    world_size = torch.cuda.device_count()
    
    manager = mp.Manager()
    return_dict = manager.dict()

    mp.spawn(
        run_inference,
        args=(world_size, model_name_or_path, prompts, return_dict),
        nprocs=world_size,
        join=True
    )
    
    # Process the results here
    # For example, to print all results:
    for rank_results in return_dict.values():
        if rank_results is not None:
            for prompt, response in rank_results:
                print(f"Prompt: {prompt}\nResponse: {response}\n")

if __name__ == "__main__":
    main()
