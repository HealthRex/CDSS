from functools import partial
import requests
import json
import time
import os 

class API_text_to_text:
    def __init__(self, model_init, model_call):
        self.model_init = model_init
        self.model_call = model_call
        self.model_init_dict = model_init()
        
    def gen_txt_to_txt(self, input_txt):
        return self.model_call(input_txt, **self.model_init_dict)
    
def error_handling(model_name, i, max_calls, sleep_time, e):
            print(f"Failed with {model_name} (SHC) call {i}/{max_calls}, waited {i*sleep_time} seconds. Error: {e}.")
            time.sleep(sleep_time)
            return f"Failed to get a response from {model_name} (SHC) after {i*sleep_time} seconds. Error: {e}."
    
# Gemini via Vertex AI
def gemini_init(model_name, credentials_path):
    # For HIPAA compliance, everything remains in our Google Cloud Project
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'
    from vertexai.preview.generative_models import GenerativeModel
    return {"ready_model": GenerativeModel(model_name), "model_name": model_name}

def gemini_call(input_txt, max_calls = 10, sleep_time = 5, **kwargs):
    ready_model = kwargs["ready_model"]
    model_name = kwargs["model_name"]
    
    for i in range (max_calls):
        try:
            response = ready_model.generate_content([input_txt])
            full_response = response.candidates[0].content.parts[0].text
            break
        except Exception as e:
            full_response = error_handling(model_name, i, max_calls, sleep_time, e)
    return full_response

# Gemini 2.5 Pro via SHC
def gemini_shc_init(model_name, my_key):
    headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}
    url = 'https://apim.stanfordhealthcare.org/gemini-25-pro/gemini-25-pro'
    return {"model_name": model_name, "url": url, "headers": headers}

def gemini_shc_call(input_txt, max_calls=10, sleep_time=5, **kwargs):
    model_name = kwargs["model_name"]
    url = kwargs["url"]
    headers = kwargs["headers"]
    payload = json.dumps({"contents": [{"role": "user", "parts": [{ "text": input_txt }]}]})
    
    for i in range(max_calls):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            full_response = ''.join([i['candidates'][0]['content']['parts'][0]['text'] for i in json.loads(response.text)])
            break
        except Exception as e:
            full_response = error_handling(model_name, i, max_calls, sleep_time, e)
    return full_response

# Open AI models via SHC
def openai_init(model_name, my_key):
    headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}
    # Use correct API version for GPT-5 deployments
    if model_name.startswith("gpt-5"):
        url = f"https://apim.stanfordhealthcare.org/openai-eastus2/deployments/{model_name}/chat/completions?api-version=2024-12-01-preview"
    else:
        url = f"https://apim.stanfordhealthcare.org/openai-eastus2/deployments/{model_name}/chat/completions?api-version=2025-01-01-preview"
    if model_name == "gpt-4o":
        url = "https://apim.stanfordhealthcare.org/openai20/deployments/gpt-4o/chat/completions?api-version=2023-05-15" 
    return {"model_name": model_name, "url": url, "headers": headers}

def openai_call(input_txt, max_calls = 10, sleep_time = 5, **kwargs):
    model_name = kwargs["model_name"]
    url = kwargs["url"]
    headers = kwargs["headers"]
    payload = json.dumps({"model": model_name, "messages": [{"role": "user", "content": input_txt}]})
    for i in range(max_calls):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            full_response = json.loads(response.text)['choices'][0]['message']['content']
            break
        except Exception as e:
           full_response = error_handling(model_name, i, max_calls, sleep_time, e)
    return full_response

# Deepseek-R1 via SHC
def deepseek_init(model_name, my_key, view_thinking=False):
    _ = model_name # There is only deepseek R1 available to us at deepseek
    headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}
    url = "https://apim.stanfordhealthcare.org/deepseekr1/v1/chat/completions"
    return {"url": url, "headers": headers, "view_thinking": view_thinking}

def deepseek_call(input_txt, max_calls = 10, sleep_time = 5, **kwargs):
    url = kwargs["url"]
    headers = kwargs["headers"]
    payload = json.dumps({"model": "deepseek-chat", "messages": [{"role": "user", "content": input_txt}], "temperature": 0.8, "max_tokens": 4096, "top_p": 1, "stream": False})
    for i in range(max_calls):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            full_response = json.loads(response.text)['choices'][0]['message']['content']
            if kwargs["view_thinking"]:
                break
            def _extract_after_think(text):
                parts = text.split("</think>")
                return parts[1].strip() if len(parts) > 1 else text
            full_response = _extract_after_think(full_response)
            break
        except Exception as e:
            full_response = error_handling("deepseek-r1", i, max_calls, sleep_time, e)
    return full_response

# Microsoft model via SHC
def microsoft_init(model_name, my_key):
    _ = model_name # There is only Phi-3.5-mini-instruct available to us at microsoft
    headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}
    url = "https://apim.stanfordhealthcare.org/phi35mi/v1/chat/completions"
    return {"url": url, "headers": headers}

def microsoft_call(input_txt, max_calls = 10, sleep_time = 5, **kwargs):
    url = kwargs["url"]
    headers = kwargs["headers"]
    payload = json.dumps({"messages": [{"role": "user", "content": input_txt}], "max_tokens": 2048, "temperature": 0.8, "top_p": 0.1, "presence_penalty": 0, "frequency_penalty": 0, "model": "Phi-3.5-mini-instruct"})
    for i in range(max_calls):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            full_response = json.loads(response.text)["choices"][0]["message"]["content"]
            break
        except Exception as e:
            full_response = error_handling("phi-3.5-mini-instruct", i, max_calls, sleep_time, e)
    return full_response

# Anthropic model via SHC
def anthropic_init(model_name, my_key):
    if model_name == "claude-3.7-sonnet":
        url = "https://apim.stanfordhealthcare.org/awssig4claude37/aswsig4claude37"
        model_id = "arn:aws:bedrock:us-west-2:679683451337:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    elif model_name == "claude-3.5-sonnet-v2":
        url = "https://apim.stanfordhealthcare.org/Claude35Sonnetv2/awssig4fa"
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}
    return {"model_id": model_id, "url": url, "headers": headers}

def anthropic_call(input_txt, max_calls = 10, sleep_time = 5, **kwargs):
    model_id = kwargs["model_id"]
    url = kwargs["url"]
    headers = kwargs["headers"]
    payload = json.dumps({"model_id": model_id, "prompt_text": input_txt})
    for i in range(max_calls):
        try:
            response = requests.request("POST", url, headers=headers, data=payload) 
            full_response = json.loads(response.text)['content'][0]['text']
            break
        except Exception as e:
            full_response = error_handling(model_id, i, max_calls, sleep_time, e)
    return full_response

# Meta model via SHC
def meta_init(model_name, my_key):
    if model_name == "llama4-scout":
        full_model_name = "Llama-4-Scout-17B-16E-Instruct"
    elif model_name == "llama4-maverick":
        full_model_name = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    headers = {'Ocp-Apim-Subscription-Key': my_key, 'Content-Type': 'application/json'}
    url = f"https://apim.stanfordhealthcare.org/{model_name}/v1/chat/completions"
    return {"full_model_name": full_model_name, "url": url, "headers": headers}

def meta_call(input_txt, max_calls = 10, sleep_time = 5, **kwargs):
    full_model_name = kwargs["full_model_name"]
    url = kwargs["url"]
    headers = kwargs["headers"]
    payload = json.dumps({"model": full_model_name, "messages": [{"role": "user", "content": input_txt}]})
    for i in range(max_calls):
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            full_response = json.loads(response.text)['choices'][0]['message']['content']
            break
        except Exception as e:
            full_response = error_handling(full_model_name, i, max_calls, sleep_time, e)
    return full_response

if __name__ == "main":
    from dotenv import load_dotenv
    load_dotenv("../../../.env")
    
    my_question = """First, state what LLM you are based on. Please answer with the precise version of the model.
    Next, answer the following hard physics question.
    What is the difference between the cosmological constant and the vacuum energy?"""
    
    lab_key = os.getenv("LAB_KEY") # enter the lab key here
    
    # Using Gemini 2.5 pro via SHC
    gemini_shc_init_partial = partial(gemini_shc_init, "gemini-2.5-pro-preview-05-06", lab_key)
    gemini_shc_instance = API_text_to_text(gemini_shc_init_partial, gemini_shc_call)
    res = gemini_shc_instance.gen_txt_to_txt(my_question)
    print(res)
    
    # Using Meta via SHC
    llama_init = partial(meta_init, "llama4-maverick", lab_key)
    llama_instance = API_text_to_text(llama_init, meta_call)
    res = llama_instance.gen_txt_to_txt(my_question)
    print(res)
    
    # Using Phi via SHC
    phi_init = partial(microsoft_init, "phi-3.5-mini-instruct", lab_key)
    phi_instance = API_text_to_text(phi_init, microsoft_call)
    res = phi_instance.gen_txt_to_txt(my_question)
    print(res)
    
    # Using Claude via SHC
    claude_init = partial(anthropic_init, "claude-3.7-sonnet", lab_key)
    claude_instance = API_text_to_text(claude_init, anthropic_call)
    res = claude_instance.gen_txt_to_txt(my_question)
    print(res)
    
    # Using Deepseek via SHC
    r1_init = partial(deepseek_init, "deepseek-r1", lab_key, view_thinking=True)
    deepseek_instance = API_text_to_text(r1_init, deepseek_call)
    res = deepseek_instance.gen_txt_to_txt(my_question)
    print(res)

    # Using OpenAI models via SHC (GPT-5 example)
    gpt5_init = partial(openai_init, "gpt-5", lab_key)
    openai_instance = API_text_to_text(gpt5_init, openai_call)
    res = openai_instance.gen_txt_to_txt(my_question)
    print(res)
    
    # Using Gemini via Vertex AI
    credentials_path = "../../mykeys/grolleau_application_default_credentials.json"
    
    gemini25 = partial(gemini_init, "gemini-2.5-pro-preview-03-25", credentials_path)        
    gemini_instance = API_text_to_text(gemini25, gemini_call)
    res = gemini_instance.gen_txt_to_txt(my_question)
    print(res)
