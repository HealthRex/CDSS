import json
import requests
import time
import aiohttp
import asyncio
import json
from .llm_models import MODEL_GPT_O3_MINI
from config import LLM_O3_MINI_API_URL
from config import LLM_API_KEY


def get_default_api_header():
    # Common Headers (Used for all models)
    headers = {'Ocp-Apim-Subscription-Key': LLM_API_KEY, 'Content-Type': 'application/json'}
    
    return headers

async def call_gpt_o3_mini(prompt, max_calls=10, sleep_time=5, logger=None):
    url = LLM_O3_MINI_API_URL
    headers = get_default_api_header()
    payload = {
        "model": "o3-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    for i in range(max_calls):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 429:
                        wait_time = 70
                        await asyncio.sleep(wait_time)
                        continue
                    if response.status == 200:
                        data = await response.json()
                        final_data = data["choices"][0]["message"]["content"]
                        # logger.write(f'Raw LLM output response data:{data}'+ "\n")
                        # logger.write(f'Raw LLM output response final data:{final_data}')
                        return final_data 
                    raise Exception(f"Status {response.status}: {await response.text()}")
        except Exception as e:
            msg = f"[gpt_o3_mini] Retry {i+1}/{max_calls}, Error: {e}"
            if logger:
                logger.write(msg + "\n")
                logger.flush()
            else:
                print(msg)
            if i < max_calls - 1:
                await asyncio.sleep(sleep_time)

    error_msg = f"[gpt_o3_mini] Failed after {max_calls} attempts."
    if logger:
        logger.write(error_msg + "\n")
        logger.flush()
    else:
        print(error_msg)
    return error_msg

_MODEL_HANDLERS = {
    MODEL_GPT_O3_MINI: call_gpt_o3_mini
}

async def generate_response(model=MODEL_GPT_O3_MINI, prompt="", max_calls=10, sleep_time=5, logger=None):
    if model not in _MODEL_HANDLERS:
        raise ValueError(f"Unsupported model '{model}'")
    return await _MODEL_HANDLERS[model](prompt=prompt, max_calls=max_calls, sleep_time=sleep_time, logger=logger)
