from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import torch
import json
import os
try : 
    os.chdir("/home/grolleau/discharge_sum_proj/scripts")
except:
    pass

#read pickle file
final_df = pd.read_pickle('../pickle/final_df.pkl')

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

def make_prompt_1(item_n, ds, fill=None):
    if fill is None:
        fill = to_extract[item_n]
    prompt_1 = f"""
    You are an internal medicine specialist with extensive expertise in computer science. Your task is to read the following discharge summary from the patient's inpatient stay and to provide an ideal, more professional rephrasing of the "{fill}." Output the response as valid JSON in the following format: 

    {{
    "explanation": str,
    "ideal_response_for_the_{fill.replace(' ', '_')}": str
    }}

    Guidelines:
    - Use a step-by-step reasoning approach.
    - Summarize your thought process in the "explanation" field.
    - Ensure each field is no longer than two sentences.
    - Use keywords rather than full sentences for the response field when possible.
    - Do NOT nest a JSON object within another JSON object.
    - Close the JSON object with a curly bracket `{"}"}`.
    - Provide no additional text after the JSON object.

    --- START discharge summary ---
    {ds}
    -- END discharge summary ---
    """
    return prompt_1

def make_prompt_2(item_n, fill=None):
    if fill is None:
        fill = to_extract[item_n]
    prompt_2 = f"""
    Can you provide a fair, but less professional rephrasing of the "{fill}"? Make sure to include only the information provided in the 'ideal_response_for_the_{fill.replace(' ', '_')}', while omitting some of the less important details. Do not add any new information. Output the response as valid JSON in the following format:

    {{
    "explanation": str,
    "fair_response_for_the_{fill.replace(' ', '_')}": str
    }}

    Guidelines:
    - Use a step-by-step reasoning approach.
    - Summarize your thought process in the "explanation" field.
    - Ensure each field is no longer than two sentences.
    - Use keywords rather than full sentences for the response field when possible.
    - Do NOT nest a JSON object within another JSON object.
    - Close the JSON object with a curly bracket `{"}"}`.
    - Provide no additional text after the JSON object.
    """
    return prompt_2

def make_prompt_3(item_n, fill=None):
    if fill is None:
        fill = to_extract[item_n]
    prompt_3 = f"""
    Can you create plausible yet incorrect keywords for the "{fill}" that a careless medical student might note for this patient? The medical terminology should remain precise, but ALL keywords mentioned should be incorrect. Output the response as valid JSON in the following format:

    {{
    "explanation": str,
    "wrong_keywords_for_the_{fill.replace(' ', '_')}": str
    }}

    Guidelines:
    - Use a step-by-step reasoning approach.
    - Summarize your thought process in the "explanation" field.
    - Ensure each field is no longer than two sentences.
    - Use keywords rather than full sentences for the response field.
    - Do NOT nest a JSON object within another JSON object.
    - Close the JSON object with a curly bracket `{"}"}`.
    - Provide no additional text after the JSON object.
    """
    return prompt_3

#ds_example = """Stanford Health Care   Discharge Summary blablabla blablabla blablabla"""
#print(make_prompt_1(0, ds_example))
#print(make_prompt_2(0))
#print(make_prompt_3(0))

def make_llama_3_prompt(user, system="You are a helpful AI assistant with extensive knowledge in internal medicine and computer science."):
    system_prompt = ""
    if system != "":
        system_prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n{system}"
            f"<|eot_id|>"
        )
    prompt = (f"{system_prompt}" # <|begin_of_text|> is not needed as it is added by left padding in the tokenizer
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{user}"
                f"<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )
    begin_res = "{\n" + '"explanation": "'
    return prompt + begin_res 

def make_first_prompts_qi(q_i, start_i, batch_size):
    # q_i is the index of the question to ask (in to_extract)
    # batch_size is the number of prompts to generate
    return [make_llama_3_prompt(make_prompt_1(q_i, final_df.iloc[start_i + i]['truncated_d_c_summaries'])) for i in range(batch_size)]

def generate_from_prompts(prompts):
    model_inputs = tokenizer(prompts, padding=True, return_tensors="pt").to("cuda")
    generated_ids = model.generate(**model_inputs, max_new_tokens=300)
    res = tokenizer.batch_decode(generated_ids, skip_special_tokens=False)
    return res

def get_json(x, i): 
    # x is the response from the model
    # i is the the prompt iteration ie (0,1,2) for (first, second, third) for (ideal, fair, wrong)
    try: 
        temp = '{"explanation": "' + x.split('"explanation": "')[i+1].split('<|eot_id|>')[0].lower()
        # If temp does not end with a curly bracket, add one
        if temp[-1] != "}":
            temp += "}"
        return temp.replace('\n', ' ')
    except:
        return None

def ex_to_json(x):
    try:
        return json.loads(x)
    except:
        return {}

def make_llama_3_followup(previous, new_question):
    ref_previous = previous.split('<|begin_of_text|>')[1].split('<|end_of_text|>')[0]
    ref_new_question = (f"<|eot_id|>"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{new_question}"
                f"<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )
    begin_res = "{\n" + '"explanation": "'
    return ref_previous + ref_new_question + begin_res

def make_second_prompts_qi(q_i, previous_res):
    # q_i is the index of the question to ask (in to_extract)
    return [make_llama_3_followup(x, make_prompt_2(q_i)) for x in previous_res]

def make_third_prompts_qi(q_i, previous_res):
    # q_i is the index of the question to ask (in to_extract)
    return [make_llama_3_followup(x, make_prompt_3(q_i)) for x in previous_res]

def generate_sequentially(q_i, start_i, batch_size):
    prompts = make_first_prompts_qi(q_i, start_i, batch_size)
    torch.cuda.empty_cache() 
    res_1 = generate_from_prompts(prompts)
    torch.cuda.empty_cache()
    res_2 = generate_from_prompts(make_second_prompts_qi(q_i, res_1))
    torch.cuda.empty_cache()
    res_3 = generate_from_prompts(make_third_prompts_qi(q_i, res_2))
    return res_1, res_2, res_3

# create a dataframe to store the results
all_columns = sum([["ideal_response_for_the_" + j, "fair_response_for_the_" + j, "wrong_keywords_for_the_" + j] for j in [i.replace(' ', '_') for i in to_extract]], [])
llm_prefill = pd.DataFrame(np.full((len(final_df), len(all_columns)), np.nan), columns=all_columns).fillna('Not extracted yet')

def run_inference(batch_size):
    # create a log file with date and time in the name
    start_time = datetime.now(pytz.timezone('US/Pacific')).strftime("%Y%m%d_%H%M%S")
    log_file_path = f"../logs/{start_time}.txt"
    with open(log_file_path, "w") as f:
        f.write(f"At {str(datetime.now(pytz.timezone('US/Pacific')))[:-13]}, started inference with {hf_model}\n")
    try:    
        # run inference
        total_batches = 1 + len(final_df) // batch_size if len(final_df) % batch_size != 0 else len(final_df) // batch_size
        for batch_no in range(total_batches):
            start_i = batch_no * batch_size

            if start_i + batch_size > len(final_df) - 1:
                batch_size = len(final_df) - start_i

            for q_i in range(len(to_extract)):
                _, _, res = generate_sequentially(q_i=q_i, start_i=start_i, batch_size=batch_size)         
                log_message = f"At {str(datetime.now(pytz.timezone('US/Pacific')))[:-13]}, completed component {q_i} out of {len(to_extract)-1} from batch no. {batch_no} out of {total_batches-1}."
                with open(log_file_path, "a") as f: f.write(log_message + "\n")
                
                for i in range(batch_size):
                    for ifw in range(3): # ifw: ideal, fair, wrong
                        try:
                            extracted_json = [v for k, v in ex_to_json(get_json(res[i], ifw)).items() if k != "explanation"][0]
                            llm_prefill.iloc[start_i + i, 3 * q_i + ifw] = extracted_json
                        except:
                            log_message = f"At {str(datetime.now(pytz.timezone('US/Pacific')))[:-13]}, failed to produce a valid JSON for id no. {batch_no * batch_size + i}, component {q_i}, ifw {ifw}, incorrect output: {res[i]}"
                            with open(log_file_path, "a") as f: f.write(log_message + "\n")
                            llm_prefill.iloc[start_i + i, 3 * q_i + ifw] = "LLM failed to produce a valid JSON."
            
            log_message = f"At {str(datetime.now(pytz.timezone('US/Pacific')))[:-13]}, COMPLETED BATCH NO. {batch_no} OUT OF {total_batches-1}."
            with open(log_file_path, "a") as f: f.write(log_message + "\n")
            
            # save the dataframe as a pickle file after all components q_i are completed for a batch
            llm_prefill.to_pickle(f'../pickle/llm_prefill_{start_time}.pkl')
    except Exception as e:
        log_message = f"At {str(datetime.now(pytz.timezone('US/Pacific')))[:-13]}, an error occurred: {str(e)}"
        with open(log_file_path, "a") as f: f.write(f"At {str(datetime.now(pytz.timezone('US/Pacific')))[:-13]}, an error occurred: {str(e)}")

if __name__ == "__main__":
    hf_model = "meta-llama/Llama-3.1-8B-Instruct" # Model we want to use
    #hf_model = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF" # this model is too large/slow/expensive to run for now
    #hf_model = "meta-llama/Llama-3.2-1B-Instruct" # small model for testing
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    model = AutoModelForCausalLM.from_pretrained(hf_model, device_map="auto", quantization_config=bnb_config, cache_dir="../../.cache/huggingface/hub")
    tokenizer = AutoTokenizer.from_pretrained(hf_model, padding_side="left")
    tokenizer.pad_token = tokenizer.eos_token  
    
    run_inference(batch_size=48)
    os.system('sudo shutdown -h now') # Shutdown computer after script is done running or if there is an error
    
    # load the pickle file
    #llm_prefill = pd.read_pickle('../pickle/llm_prefill_XXXX_XXX.pkl')
    
    # nohup python prefill_with_llm.py &
    # tail -f nohup.out
    # cd ../logs/ 
    # tail -f [logfilename.txt] | cut -c 1-100
    # watch -n 1 nvidia-smi