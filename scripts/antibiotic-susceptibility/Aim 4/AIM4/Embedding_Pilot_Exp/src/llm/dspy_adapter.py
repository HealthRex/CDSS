import dspy
import asyncio
import logging
import os
import sys
import threading
import nest_asyncio
from .llm_client import generate_response
from .model_registry import MODEL_CONFIGS

# Apply nest_asyncio to allow nested event loops (crucial for calling async code from sync DSPy)
try:
    nest_asyncio.apply()
except Exception:
    pass

# Thread-local storage for logging context (index, code_key, etc.)
_log_context = threading.local()

def set_log_context(index=None, code_key=None):
    """Set the current logging context (called before classifier runs)."""
    _log_context.index = index
    _log_context.code_key = code_key

def get_log_context_str() -> str:
    """Get formatted context string for logging."""
    parts = []
    if hasattr(_log_context, 'index') and _log_context.index is not None:
        parts.append(f"Index={_log_context.index}")
    if hasattr(_log_context, 'code_key') and _log_context.code_key is not None:
        parts.append(f"Code={_log_context.code_key}")
    return f" ({', '.join(parts)})" if parts else ""

def _log_prompt(prefix: str, content: str):
    """Log prompt to console and optionally to file."""
    # Read env vars dynamically (they may be set after module import)
    verbose = os.environ.get("DSPY_VERBOSE", "0") == "1"
    prompt_log_file = os.environ.get("DSPY_PROMPT_LOG", None)
    
    # Add context (index, code_key) to prefix
    context_str = get_log_context_str()
    full_prefix = f"{prefix}{context_str}"
    
    if verbose:
        # Truncate for console (first 500 chars)
        truncated = content[:500] + "..." if len(content) > 500 else content
        print(f"\n{'='*60}\n[{full_prefix}]\n{truncated}\n{'='*60}", file=sys.stderr)
    
    if prompt_log_file:
        with open(prompt_log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n[{full_prefix}]\n{content}\n")


class HealthRexDSPyLM(dspy.LM):
    """
    Adapter to connect DSPy with HealthRex's custom async LLM client.
    """
    def __init__(self, model_name, **kwargs):
        super().__init__(model=model_name, **kwargs)
        self.model_name = model_name
        self.kwargs = kwargs

    def __call__(self, prompt=None, messages=None, **kwargs):
        """
        DSPy calls this method synchronously. We must bridge to our async client.
        DSPy 3.0 may pass 'messages' instead of 'prompt'.
        """
        # Merge init kwargs with call kwargs
        merged_kwargs = {**self.kwargs, **kwargs}
        
        # Handle DSPy 3.0 calling convention where it passes messages list
        final_prompt = prompt
        if final_prompt is None and messages is not None:
            # Convert messages list to string if underlying client expects string
            # messages is usually [{'role': 'user', 'content': '...'}, ...]
            # Simple strategy: Join content (or just take the last user message if that's what logic expects)
            # But usually concatenation is safer for generic "prompt" based APIs
            final_prompt = ""
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                # Simple formatting
                if role == "user":
                    final_prompt += f"{content}\n"
                elif role == "system":
                    final_prompt += f"System: {content}\n"
                else:
                    final_prompt += f"{content}\n"
        
        if final_prompt is None:
             final_prompt = ""

        # Read env vars dynamically
        verbose = os.environ.get("DSPY_VERBOSE", "0") == "1"
        prompt_log_file = os.environ.get("DSPY_PROMPT_LOG", None)

        # Log finalized prompt
        if verbose or prompt_log_file:
            _log_prompt("FINALIZED PROMPT TO LLM", final_prompt)

        # Handle event loop safely
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If loop is running, we can't use run_until_complete normally
            # But nest_asyncio patches this. 
            import nest_asyncio
            nest_asyncio.apply(loop)
            response = loop.run_until_complete(
                generate_response(model=self.model_name, prompt=final_prompt, logger=sys.stdout if verbose else None)
            )
        else:
            response = loop.run_until_complete(
                generate_response(model=self.model_name, prompt=final_prompt, logger=sys.stdout if verbose else None)
            )

        # Log response
        if verbose or prompt_log_file:
            _log_prompt("LLM RESPONSE", response if response else "(empty)")

        # DSPy expects a list of strings (completions)
        return [response]

    def request(self, prompt, **kwargs):
        # Some DSPy versions use 'request' or 'basic_request'
        return self.__call__(prompt, **kwargs)
