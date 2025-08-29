import asyncio
import aiohttp
from .llm_models import MODEL_GPT_O3_MINI, MODEL_GPT5
from config import LLM_O3_MINI_API_URL, LLM_GPT5_API_URL, LLM_API_KEY

# ---- model → URL map (add new models here) ----
MODEL_TO_URL = {
    MODEL_GPT_O3_MINI: LLM_O3_MINI_API_URL,
    MODEL_GPT5: LLM_GPT5_API_URL,
}
def get_default_api_header():
    # Common Headers (Used for all models)
    headers = {'Ocp-Apim-Subscription-Key': LLM_API_KEY, 'Content-Type': 'application/json'}
    
    return headers

async def call_llm(model, url, prompt, max_calls=10, sleep_time=5, logger=None):
    headers = get_default_api_header()
    payload = {
        # Azure deployment endpoints usually don't need "model", but your lab examples include it.
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Reuse one session across retries (simple, minimal change)
    async with aiohttp.ClientSession() as session:
        for i in range(max_calls):
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 429:
                        wait_time = 70  # keep your current behavior
                        if logger:
                            logger.write(f"[{model}] 429 received. Sleeping {wait_time}s (retry {i+1}/{max_calls}).\n")
                            logger.flush()
                        await asyncio.sleep(wait_time)
                        continue

                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]

                    # Non-200
                    raise Exception(f"Status {response.status}: {await response.text()}")

            except Exception as e:
                msg = f"[{model}] Retry {i+1}/{max_calls}, Error: {e}"
                if logger:
                    logger.write(msg + "\n")
                    logger.flush()
                else:
                    print(msg)
                if i < max_calls - 1:
                    await asyncio.sleep(sleep_time)

    error_msg = f"[{model}] Failed after {max_calls} attempts."
    if logger:
        logger.write(error_msg + "\n")
        logger.flush()
    else:
        print(error_msg)
    return error_msg


async def generate_response(model=MODEL_GPT5, prompt="", max_calls=10, sleep_time=5, logger=None):
    # Pick the correct URL for the chosen model (no need to pass url from caller)
    if model not in MODEL_TO_URL:
        raise ValueError(f"Unsupported model '{model}'")
    url = MODEL_TO_URL[model]
    return await call_llm(model=model, url=url, prompt=prompt, max_calls=max_calls, sleep_time=sleep_time, logger=logger)
