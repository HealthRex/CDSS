"""
Model Registry: Centralized configuration for all LLM models.

Based on the agnostic_evaluator_models.py reference implementation.

Each model defines:
- url: The API endpoint URL (or url_builder for dynamic URLs)
- build_payload: Function to construct the request payload
- parse_response: Function to extract content from the response

To add a new model:
1. Define payload builder and response parser functions
2. Add ModelConfig to MODEL_CONFIGS dict
3. Add the URL to your .env file (if using env var)
"""
import json
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Optional


@dataclass
class ModelConfig:
    """Configuration for a single LLM model."""
    url: str  # API endpoint URL
    build_payload: Callable[[str, str], Dict[str, Any]]  # (model_name, prompt) -> payload dict
    parse_response: Callable[[Dict[str, Any]], str]  # response_json -> content string
    display_name: str  # Human-readable name


# ---------- Payload Builders ----------

def build_openai_payload(model: str, prompt: str) -> Dict[str, Any]:
    """OpenAI/Azure OpenAI format (GPT-4, GPT-5, O3, etc.)"""
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }


def build_claude_37_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Claude 3.7 Sonnet via AWS Bedrock."""
    return {
        "model_id": "arn:aws:bedrock:us-west-2:679683451337:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "prompt_text": prompt,
    }


def build_claude_35_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Claude 3.5 Sonnet v2 via AWS Bedrock."""
    return {
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "prompt_text": prompt,
    }


def build_gemini_25_pro_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Gemini 2.5 Pro format."""
    return {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }


def build_gemini_20_flash_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Gemini 2.0 Flash format with safety settings."""
    return {
        "contents": {"role": "user", "parts": {"text": prompt}},
        "safety_settings": {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        "generation_config": {"temperature": 0.2, "topP": 0.8, "topK": 40},
    }


def build_deepseek_payload(model: str, prompt: str) -> Dict[str, Any]:
    """DeepSeek R1 format."""
    return {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 4096,
        "top_p": 1,
        "stream": False,
    }


def build_phi_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Microsoft Phi 3.5 Mini format."""
    return {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "temperature": 0.8,
        "top_p": 0.1,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "model": "Phi-3.5-mini-instruct",
    }


def build_llama4_scout_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Meta Llama 4 Scout format."""
    return {
        "model": "Llama-4-Scout-17B-16E-Instruct",
        "messages": [{"role": "user", "content": prompt}],
    }


def build_llama4_maverick_payload(model: str, prompt: str) -> Dict[str, Any]:
    """Meta Llama 4 Maverick format."""
    return {
        "model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": [{"role": "user", "content": prompt}],
    }


# ---------- Response Parsers ----------

def parse_openai_response(data: Dict[str, Any]) -> str:
    """Parse OpenAI/Azure OpenAI response."""
    return data["choices"][0]["message"]["content"]


def parse_claude_response(data: Dict[str, Any]) -> str:
    """Parse Claude/Bedrock response: data['content'][0]['text']"""
    return data["content"][0]["text"]


def parse_gemini_response(data: Dict[str, Any]) -> str:
    """
    Parse Gemini response.
    The response may be a list, so join all candidates.
    Format: join([i['candidates'][0]['content']['parts'][0]['text'] for i in response])
    """
    # Handle case where response is a list of objects
    if isinstance(data, list):
        texts = []
        for item in data:
            try:
                texts.append(item['candidates'][0]['content']['parts'][0]['text'])
            except (KeyError, IndexError, TypeError):
                pass
        return ''.join(texts)
    
    # Handle single object response
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return f"[PARSE_ERROR] Unknown response format: {json.dumps(data)[:500]}"


def parse_deepseek_response(data: Dict[str, Any], strip_thinking: bool = True) -> str:
    """
    Parse DeepSeek R1 response.
    Optionally strips the <think>...</think> section.
    """
    content = data["choices"][0]["message"]["content"]
    
    if strip_thinking and "</think>" in content:
        parts = content.split("</think>")
        return parts[1].strip() if len(parts) > 1 else content
    
    return content


def parse_deepseek_with_thinking(data: Dict[str, Any]) -> str:
    """Parse DeepSeek R1 response, keeping the thinking section."""
    return parse_deepseek_response(data, strip_thinking=False)


# ---------- Model Configurations ----------

MODEL_CONFIGS: Dict[str, ModelConfig] = {
    # OpenAI models
    "gpt-5": ModelConfig(
        url="https://apim.stanfordhealthcare.org/openai-eastus2/deployments/gpt-5/chat/completions?api-version=2024-12-01-preview",
        build_payload=build_openai_payload,
        parse_response=parse_openai_response,
        display_name="GPT-5 (Azure OpenAI)",
    ),
    "gpt-5-mini": ModelConfig(
        url="https://apim.stanfordhealthcare.org/openai-eastus2/deployments/gpt-5-mini/chat/completions?api-version=2024-12-01-preview",
        build_payload=build_openai_payload,
        parse_response=parse_openai_response,
        display_name="GPT-5 Mini (Azure OpenAI)",
    ),
    "gpt-4o": ModelConfig(
        url="https://apim.stanfordhealthcare.org/openai20/deployments/gpt-4o/chat/completions?api-version=2023-05-15",
        build_payload=build_openai_payload,
        parse_response=parse_openai_response,
        display_name="GPT-4o (Azure OpenAI)",
    ),
    "o3-mini": ModelConfig(
        url="https://apim.stanfordhealthcare.org/openai-eastus2/deployments/o3-mini/chat/completions?api-version=2025-01-01-preview",
        build_payload=build_openai_payload,
        parse_response=parse_openai_response,
        display_name="O3-Mini (Azure OpenAI)",
    ),
    
    # Claude models (AWS Bedrock)
    "claude-3.7-sonnet": ModelConfig(
        url="https://apim.stanfordhealthcare.org/awssig4claude37/aswsig4claude37",
        build_payload=build_claude_37_payload,
        parse_response=parse_claude_response,
        display_name="Claude 3.7 Sonnet (AWS Bedrock)",
    ),
    "claude-3.5-sonnet-v2": ModelConfig(
        url="https://apim.stanfordhealthcare.org/Claude35Sonnetv2/awssig4fa",
        build_payload=build_claude_35_payload,
        parse_response=parse_claude_response,
        display_name="Claude 3.5 Sonnet v2 (AWS Bedrock)",
    ),
    
    # Gemini models
    "gemini-2.5-pro": ModelConfig(
        url="https://apim.stanfordhealthcare.org/gemini-25-pro/gemini-25-pro",
        build_payload=build_gemini_25_pro_payload,
        parse_response=parse_gemini_response,
        display_name="Gemini 2.5 Pro",
    ),
    "gemini-2.0-flash": ModelConfig(
        url="https://apim.stanfordhealthcare.org/gcp-gem20flash-fa/apim-gcp-gem20flash-fa",
        build_payload=build_gemini_20_flash_payload,
        parse_response=parse_gemini_response,
        display_name="Gemini 2.0 Flash",
    ),
    
    # DeepSeek
    "deepseek-r1": ModelConfig(
        url="https://apim.stanfordhealthcare.org/deepseekr1/v1/chat/completions",
        build_payload=build_deepseek_payload,
        parse_response=parse_deepseek_response,
        display_name="DeepSeek R1",
    ),
    "deepseek-r1-thinking": ModelConfig(
        url="https://apim.stanfordhealthcare.org/deepseekr1/v1/chat/completions",
        build_payload=build_deepseek_payload,
        parse_response=parse_deepseek_with_thinking,
        display_name="DeepSeek R1 (with thinking)",
    ),
    
    # Microsoft
    "phi-3.5-mini": ModelConfig(
        url="https://apim.stanfordhealthcare.org/phi35mi/v1/chat/completions",
        build_payload=build_phi_payload,
        parse_response=parse_openai_response,  # Same format as OpenAI
        display_name="Phi 3.5 Mini (Microsoft)",
    ),
    
    # Meta Llama
    "llama4-scout": ModelConfig(
        url="https://apim.stanfordhealthcare.org/llama4-scout/v1/chat/completions",
        build_payload=build_llama4_scout_payload,
        parse_response=parse_openai_response,  # Same format as OpenAI
        display_name="Llama 4 Scout (Meta)",
    ),
    "llama4-maverick": ModelConfig(
        url="https://apim.stanfordhealthcare.org/llama4-maverick/v1/chat/completions",
        build_payload=build_llama4_maverick_payload,
        parse_response=parse_openai_response,  # Same format as OpenAI
        display_name="Llama 4 Maverick (Meta)",
    ),
}


def get_model_config(model_alias: str) -> ModelConfig:
    """Get configuration for a model by alias."""
    if model_alias not in MODEL_CONFIGS:
        available = ", ".join(MODEL_CONFIGS.keys())
        raise ValueError(f"Unknown model '{model_alias}'. Available: {available}")
    return MODEL_CONFIGS[model_alias]


def list_available_models() -> None:
    """Print all available models and their status."""
    print("\n" + "="*70)
    print("Available Models")
    print("="*70)
    for alias, config in MODEL_CONFIGS.items():
        print(f"  {alias:<22} {config.display_name}")
    print("="*70 + "\n")
