from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from functools import partial
import torch
import json
import pandas as pd
from scripts.database_extraction.pivoted_notes import final_df # Takes ~ 3 minutes to run

def make_llama_3_prompt(user, system=""):
    system_prompt = ""
    if system != "":
        system_prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n{system}"
            f"<|eot_id|>"
        )
    prompt = (f"<|begin_of_text|>{system_prompt}"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{user}"
                f"<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )
    return prompt  

hf_model = "meta-llama/Llama-3.2-3B-Instruct"

model = AutoModelForCausalLM.from_pretrained(hf_model, device_map="auto", load_in_4bit=True, cache_dir="../../.cache/huggingface/")
tokenizer = AutoTokenizer.from_pretrained(hf_model, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token  

to_extract = ["reason for admission", "relevant medical and surgical history", "primary and secondary diagnoses", "key investigations and results", "procedures performed", "social context", "plan for follow up", "medications changed during admission and the indications for this", "medications to be reviewed by the primary care physician and why", "actions the primary care physician should take post discharge"]

def llama3_ds_prompt(ds_no, df, target):
    system = f'''
    You are a highly skilled internal medicine doctor and an expert in computer science.
    Your task is to read the following discharge summary from an inpatient stay and identify the {target}.
    Respond with valid JSON in the format:
    {{
        "explanation": str, 
        "{target.replace(' ', '_')}": str
    }}
    
    - Use a step-by-step reasoning process, summarizing your thought process in the "explanation" field. 
    - Keep each field to a maximum length of two sentences.
    - If information is not available, use null.
    - Do not make up any information.
    - Complete the JSON object with a curly bracket `{"}"}`.
    - Include no text after the JSON object is completed.
    
    '''
    user_prompt = f'''
    --- START discharge summary ---
    {df['truncated_d_c_summaries'].iloc[ds_no]}
    --- END discharge summary ---
    '''
    start_answer = '''
    {
        "explanation": "'''
        
    res = make_llama_3_prompt(user_prompt, system=system) + start_answer
    
    return  res

# Example prompt
print(llama3_ds_prompt(0, final_df, to_extract[0]))

# Make list of prompts for the "reason for admission" target
prompts = list(map(partial(llama3_ds_prompt, df = final_df, target = to_extract[2]), range(0, 5)))
model_inputs = tokenizer(prompts, padding=True, return_tensors="pt").to("cuda")
generated_ids = model.generate(**model_inputs, max_new_tokens=600)
res = tokenizer.batch_decode(generated_ids, skip_special_tokens=False)

def get_json(x): 
    try: 
        temp = '{"explanation": "' +  x.split('"explanation": "')[1].split('}')[0].lower() + "}"
        return temp
    except:
        return None
extracted_res = list(map(get_json, res))
def ex_to_json(x):
    try:
        return json.loads(x)
    except:
        return {}
json_res = list(map(ex_to_json, extracted_res))
df_res = pd.DataFrame(json_res)
df_res

## To empty the GPU memory
torch.cuda.empty_cache()