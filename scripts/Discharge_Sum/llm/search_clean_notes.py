from scripts.database_extraction.pivoted_notes import df
import os

os.environ["KERAS_BACKEND"] = "jax"
os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"]="1.00"

import keras_nlp
import keras

# Change the precision 
keras.config.set_dtype_policy("bfloat16")

##import huggingface_hub
# In Shell: huggingface-cli login

### Llama-3-8B-Instruct ###
from keras_nlp.models import Llama3CausalLM
llama_lm = Llama3CausalLM.from_preset("hf://meta-llama/Meta-Llama-3-8B-Instruct")

# Quantize the model to improve memory usage and speed, sacrificing minimal performance
llama_lm.quantize("int8")
llama_lm.summary() 

###
# Prepare prompts in Llama3-appropriate format

def make_tunned_prompt(system, user_prompt, model_start):
    system_prompt = ""
    if system != "":
        system_prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n\n{system}"
            f"<|eot_id|>"
        )
    prompt = (f"<|begin_of_text|>{system_prompt}"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{user_prompt}"
                f"<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
                f"{model_start}"
            )
    return prompt   

system = "You are the best internal medicine docteur ever."
user_prompt = f"""
Please read the following discharge summary from an inpatient stay and identify the reason for admission. Format your answer as shown in the example: 'The reason for admission is: "heart failure".'
--- START discharge summary ---
{df['Discharge_Transfer_Summary'].iloc[114][:1000]}
--- END discharge summary ---
"""
model_start = "The reason for admission is: \""

prompt = make_tunned_prompt(system, user_prompt, model_start)
res = llama_lm.generate(prompt)
print(res)