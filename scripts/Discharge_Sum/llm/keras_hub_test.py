import os
os.environ["KERAS_BACKEND"] = "jax"

# Allow the compiler to use 100% of the GPU memory
os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"]="1.00"

import keras_hub
import keras

# Run at half precision to improve speed, sacrificing minimal performance
keras.config.set_dtype_policy("bfloat16")

### Gemma 2, 2B Instruction Tuned ###

# Download the model
gemma_lm = keras_hub.models.GemmaCausalLM.from_preset("hf://google/gemma-2-2b-it")

# Get a summary
gemma_lm.summary() # should see ~2B parameters and ~9.74 GB

# Prepare prompts in Gemma-appropriate format
def make_gemma_2_prompt(user_prompt):    
    prompt = (  f"<start_of_turn>user\n"
                f"{user_prompt}\n"
                f"<end_of_turn>\n"
                f"<start_of_turn>model\n"
                )
    return prompt

# Ask a question
prompt = make_gemma_2_prompt("What is the nature of daylight?")
res = gemma_lm.generate(prompt, max_length=64)
print(res)

### Llama-3-8B-Instruct ###

# Download the model
llama_lm = keras_hub.models.Llama3CausalLM.from_preset("hf://meta-llama/Meta-Llama-3-8B-Instruct")

# Get a summary
llama_lm.summary() # Should show 3B parameters ~29.92 GB

# Quantize the model to improve memory usage and speed, sacrificing minimal performance
llama_lm.quantize("int8")
llama_lm.summary() # Should show 3B parameters ~7.48 GB

# Prepare prompts in Llama3-appropriate format
def make_llama_3_prompt(user, system=""):
    system_prompt = ""
    if system != "":
        system_prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n\n{system}"
            f"<|eot_id|>"
        )
    prompt = (f"<|begin_of_text|>{system_prompt}"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{user}"
                f"<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
            )
    return prompt   

# Ask a simple question
prompt = make_llama_3_prompt(user="What is the meaning of life, the universe, and everything?", 
                             system="You are a superintelligent AI.")

res = llama_lm.generate(prompt, max_length=200)
print(res)