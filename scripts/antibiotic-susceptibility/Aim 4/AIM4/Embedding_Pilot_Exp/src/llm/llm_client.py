"""
LLM Client: Unified async client for all LLM models.

Uses model_registry.py for model-specific payload/response handling.
"""
import asyncio
import aiohttp
import os
from typing import Optional

from .model_registry import get_model_config, MODEL_CONFIGS

# Default model
DEFAULT_MODEL = "gpt-5"


def get_api_key() -> str:
    """Get the API key from environment."""
    key = os.getenv("HEALTHREX_API_KEY")
    if not key:
        raise ValueError("HEALTHREX_API_KEY environment variable not set")
    return key


def get_default_headers() -> dict:
    """Common headers for all models."""
    return {
        'Ocp-Apim-Subscription-Key': get_api_key(),
        'Content-Type': 'application/json'
    }


async def call_llm(
    model: str,
    prompt: str,
    max_calls: int = 10,
    sleep_time: int = 5,
    logger=None
) -> str:
    """
    Call an LLM with automatic retry and model-specific payload handling.
    
    Args:
        model: Model alias (e.g., "gpt-5", "claude-3.7-sonnet", "gemini-2.5-pro")
        prompt: The prompt text
        max_calls: Maximum retry attempts
        sleep_time: Sleep time between retries (seconds)
        logger: Optional file-like object for logging
    
    Returns:
        The model's response content as a string
    """
    config = get_model_config(model)
    url = config.url
    
    headers = get_default_headers()
    payload = config.build_payload(model, prompt)
    
    async with aiohttp.ClientSession() as session:
        for i in range(max_calls):
            try:
                async with session.post(url, headers=headers, json=payload, timeout=120) as response:
                    if response.status == 429:
                        wait_time = 70
                        if logger:
                            logger.write(f"[{model}] 429 received. Sleeping {wait_time}s (retry {i+1}/{max_calls}).\n")
                            logger.flush()
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status == 200:
                        data = await response.json()
                        return config.parse_response(data)
                    
                    # Non-200 error
                    error_text = await response.text()
                    raise Exception(f"Status {response.status}: {error_text[:500]}")
            
            except asyncio.TimeoutError:
                msg = f"[{model}] Timeout (retry {i+1}/{max_calls})"
                if logger:
                    logger.write(msg + "\n")
                    logger.flush()
                else:
                    print(msg)
                if i < max_calls - 1:
                    await asyncio.sleep(sleep_time)
            
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


async def generate_response(
    model: str = DEFAULT_MODEL,
    prompt: str = "",
    max_calls: int = 10,
    sleep_time: int = 5,
    logger=None
) -> str:
    """
    Generate a response from the specified model.
    
    This is the main entry point for LLM calls.
    """
    return await call_llm(
        model=model,
        prompt=prompt,
        max_calls=max_calls,
        sleep_time=sleep_time,
        logger=logger
    )


# ---------- Backward Compatibility ----------
# Keep these for any code that imports them directly

from .llm_models import MODEL_GPT5, MODEL_GPT_O3_MINI
