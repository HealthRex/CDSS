from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from functools import partial
import torch
import json
import pandas as pd
import os

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

def get_json(x): 
    try: 
        temp = '{"explanation": "' +  x.split('"explanation": "')[1].split('}')[0].lower() + "}"
        return temp
    except:
        return None

def ex_to_json(x):
    try:
        return json.loads(x)
    except:
        return {}

def start_end_fun(max_len, div):
    temp = [(i*div, (i+1)*div) for i in range(max_len//div)]
    if temp[-1][1] != max_len:
        temp.append((temp[-1][1], max_len))
    return temp
    
class ExtractDischargeSummaryInfo:
    def __init__(self, model_name, df):
        self.df = df
        self.model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", load_in_4bit=True, cache_dir="../../.cache/huggingface/")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        self.tokenizer.pad_token = self.tokenizer.eos_token  
    
    def specific_extract(self, target="reason for admission", start=0, end=5):
        prompts = list(map(partial(llama3_ds_prompt, df = final_df, target = target), range(start, end)))
        model_inputs = self.tokenizer(prompts, padding=True, return_tensors="pt").to("cuda")
        generated_ids = self.model.generate(**model_inputs, max_new_tokens=600)
        res = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=False)
        extracted_res = list(map(get_json, res))
        json_res = list(map(ex_to_json, extracted_res))
        return pd.DataFrame(json_res)
        
    def extract_all(self, div):
        to_extract = ["reason for admission",
                      "relevant medical and surgical history",
                      "primary and secondary diagnoses",
                      "key investigations and results",
                      "procedures performed",
                      "social context",
                      "plan for follow up",
                      "medications changed during admission and the indications for this",
                      "medications to be reviewed by the primary care physician and why",
                      "actions the primary care physician should take post discharge"]
        start_end = start_end_fun(len(self.df), div)
        dict_of_df = {to_extract[j]: pd.DataFrame() for j in range(len(to_extract))}
        for i in start_end:
            for j in range(len(to_extract)):
                print(f"- Extracting {to_extract[j]} from discharge summaries no {i[0]} to {i[1]-1} (total {start_end[-1][1]-1})")
                dict_of_df[to_extract[j]] = pd.concat([dict_of_df[to_extract[j]], self.specific_extract(target=to_extract[j], start=i[0], end=i[1])], axis=0) 
                torch.cuda.empty_cache()
        self.full_res = pd.concat([v.iloc[:,1] for _, v in dict_of_df.items()], axis=1)
        
if __name__ == "__main__":
    try:
        from scripts.database_extraction.pivoted_notes import final_df # Takes ~ 3 minutes to run
        hf_model = "meta-llama/Llama-3.2-3B-Instruct"
        test_class = ExtractDischargeSummaryInfo(hf_model, final_df.iloc[:100,:]) # Attempt with the first 100 discharge summaries
        test_class.extract_all(10) # Run in batches of 10
        final_df_res = pd.concat([test_class.df.reset_index(drop=True), test_class.full_res.reset_index(drop=True)], axis=1)
        final_df_res.to_pickle("../exports/final_df_res.pkl")
    except:
        os.system('sudo shutdown -h now') # Uncomment to shutdown computer if there is an error
    os.system('sudo shutdown -h now') # Uncomment to shutdown computer after script is done running