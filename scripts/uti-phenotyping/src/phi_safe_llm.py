"""
PHI-safe LLM wrapper for Aim 3 UTI Phenotyping — Vertex AI backend.

All models run on Stanford's PHI-safe Vertex AI (Nero *secure* project). Auth is via
each user's own Application Default Credentials (gcloud ADC) — there are NO shared API
keys. SecureGPT / the apim.stanfordhealthcare.org gateway is retired; this replaces it.

Per-user prerequisites:
    gcloud auth application-default login
    gcloud auth application-default set-quota-project som-nero-phi-jonc101-secure
    # Stanford full-traffic VPN must be ON (PHI projects use VPC Service Controls)

Project: defaults to the Nero secure project where the models are enabled; override
with the VERTEX_PROJECT environment variable.

Model families (see vertex_ai_reference.md — GA / BAA-covered only; no OpenAI/GPT):
    Gemini  -> google.genai                (us-central1)
    Claude  -> anthropic.AnthropicVertex   (Opus=global, Sonnet/Haiku=us-east5)
    Llama   -> OpenAI-compatible endpoint  (us-east5)
"""

from __future__ import annotations

import os
import random
import re
import time
from typing import Optional

# Vertex project where the LLMs are enabled. Override with VERTEX_PROJECT.
VERTEX_PROJECT = os.getenv("VERTEX_PROJECT", "som-nero-phi-jonc101-secure")

MAX_TOKENS_DEFAULT = 4096


def _sanitize_label(value, fallback: str) -> str:
    """Vertex/GCP label values must be lowercase [a-z0-9_-], <= 63 chars."""
    v = re.sub(r"[^a-z0-9_-]", "_", str(value).lower())[:63].strip("_-")
    return v or fallback


def vertex_labels() -> dict:
    """Request labels for Vertex billing attribution (per user / per experiment).

    Attached to every LLM call so spend is attributable in GCP billing. SET your own via
    VERTEX_LABEL_USER / VERTEX_LABEL_EXPERIMENT (or edit .env). user_id defaults to the
    placeholder "your_name" so unattributed spend is obvious in the bill.
    """
    return {
        "user_id": _sanitize_label(os.getenv("VERTEX_LABEL_USER", "your_name"), "your_name"),
        "experiment": _sanitize_label(os.getenv("VERTEX_LABEL_EXPERIMENT", "uti-phenotyping"),
                                       "uti-phenotyping"),
    }

# --- model registry ---------------------------------------------------------
# Gemini: location, output-token budget, whether to disable "thinking".
#   Flash accepts thinking_budget=0; Pro REJECTS 0 (HTTP 400) -> leave unset + big budget.
_GEMINI = {
    "gemini-2.5-pro":   {"location": "us-central1", "max_tokens": 8192, "disable_thinking": False},
    "gemini-2.5-flash": {"location": "us-central1", "max_tokens": 4096, "disable_thinking": True},
}
# Claude: Vertex publisher slug + region (Opus is global; Sonnet/Haiku on us-east5).
_CLAUDE = {
    "claude-opus-4-7":   {"slug": "claude-opus-4-7@default",   "region": "global"},
    "claude-sonnet-4-6": {"slug": "claude-sonnet-4-6@default", "region": "us-east5"},
    "claude-haiku-4-5":  {"slug": "claude-haiku-4-5@20251001", "region": "us-east5"},
}
# Llama: Vertex MaaS model id (OpenAI-compatible), us-east5.
_LLAMA = {
    "llama-4-maverick": "meta/llama-4-maverick-17b-128e-instruct-maas",
    "llama-4-scout":    "meta/llama-4-scout-17b-16e-instruct-maas",
}
_LLAMA_LOCATION = "us-east5"

SUPPORTED_MODELS = tuple(_GEMINI) + tuple(_CLAUDE) + tuple(_LLAMA)


def _retry(fn, model_name, max_attempts=4, base=2.0):
    """Retry with exponential backoff + jitter; surface the last error on give-up."""
    last = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:  # transient Vertex / rate-limit / network errors
            last = e
            if attempt < max_attempts - 1:
                wait = base ** (attempt + 1) + random.uniform(0, 1)
                print(f"  [{model_name}] attempt {attempt+1}/{max_attempts} failed "
                      f"({type(e).__name__}); retrying in {wait:.1f}s")
                time.sleep(wait)
    raise RuntimeError(f"All {max_attempts} attempts failed for {model_name}: {last}")


class PHISafeLLM:
    """
    PHI-safe multi-model LLM client on Stanford Vertex AI.

    Supported models:
        Gemini : gemini-2.5-pro (default), gemini-2.5-flash
        Claude : claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5
        Llama  : llama-4-maverick, llama-4-scout

    Usage:
        llm = PHISafeLLM(model_name="gemini-2.5-pro")
        text = llm.generate("Summarize this note ...", system_prompt="You are a clinician.")
    """

    def __init__(self, model_name: str = "gemini-2.5-pro", project: Optional[str] = None):
        self.model_name = model_name
        self.project = project or VERTEX_PROJECT
        self.labels = vertex_labels()   # Vertex billing attribution, attached to every call

        if model_name in _GEMINI:
            self._family = "gemini"
            self._cfg = _GEMINI[model_name]
            from google import genai
            self._client = genai.Client(vertexai=True, project=self.project,
                                        location=self._cfg["location"])
        elif model_name in _CLAUDE:
            self._family = "claude"
            self._cfg = _CLAUDE[model_name]
            from anthropic import AnthropicVertex
            self._client = AnthropicVertex(project_id=self.project, region=self._cfg["region"])
        elif model_name in _LLAMA:
            self._family = "llama"
            self._cfg = {"model_id": _LLAMA[model_name], "location": _LLAMA_LOCATION}
            import google.auth
            self._creds, _ = google.auth.default()
        else:
            raise ValueError(f"Unsupported model: {model_name}. Supported: {SUPPORTED_MODELS}")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return _retry(lambda: self._generate_once(prompt, system_prompt), self.model_name)

    # -- per-family implementations -----------------------------------------

    def _generate_once(self, prompt: str, system_prompt: Optional[str]) -> str:
        if self._family == "gemini":
            return self._gemini(prompt, system_prompt)
        if self._family == "claude":
            return self._claude(prompt, system_prompt)
        return self._llama(prompt, system_prompt)

    def _gemini(self, prompt: str, system_prompt: Optional[str]) -> str:
        from google.genai import types
        kw = {"temperature": 0.0, "max_output_tokens": self._cfg["max_tokens"]}
        if system_prompt:
            kw["system_instruction"] = system_prompt
        if self._cfg["disable_thinking"]:
            kw["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        kw["labels"] = self.labels       # billing attribution: {user_id, experiment}
        resp = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**kw),
        )
        return (resp.text or "").strip()

    def _claude(self, prompt: str, system_prompt: Optional[str]) -> str:
        # NB: Vertex's Anthropic endpoint rejects a `labels` field ("Extra inputs are not
        # permitted"), so — unlike Gemini/Llama — Claude calls carry no GCP billing label.
        kw = {
            "model": self._cfg["slug"],
            "max_tokens": MAX_TOKENS_DEFAULT,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kw["system"] = system_prompt
        # temperature is deprecated on Opus 4.7+ (HTTP 400) — don't pass it.
        msg = self._client.messages.create(**kw)
        return msg.content[0].text.strip()

    def _llama(self, prompt: str, system_prompt: Optional[str]) -> str:
        import google.auth.transport.requests
        from openai import OpenAI
        if not self._creds.valid:   # ADC token expires (~1h) — refresh as needed
            self._creds.refresh(google.auth.transport.requests.Request())
        loc = self._cfg["location"]
        client = OpenAI(
            base_url=(f"https://{loc}-aiplatform.googleapis.com/v1beta1/"
                      f"projects/{self.project}/locations/{loc}/endpoints/openapi"),
            api_key=self._creds.token,
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=self._cfg["model_id"], max_tokens=MAX_TOKENS_DEFAULT, messages=messages,
            extra_body={"labels": self.labels},   # Vertex billing attribution
        )
        return resp.choices[0].message.content.strip()
