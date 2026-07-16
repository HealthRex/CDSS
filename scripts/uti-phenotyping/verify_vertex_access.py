#!/usr/bin/env python3
"""
Smoke-test Vertex AI access for the models this pipeline can use.

Run with YOUR OWN Google Cloud credentials (Application Default Credentials) — each
user authenticates as themselves; there are no shared API keys.

Prerequisites (one-time):
    gcloud auth application-default login
    gcloud auth application-default set-quota-project <project>
    # Stanford full-traffic VPN must be ON (PHI projects use VPC Service Controls)
    pip install -r requirements.txt

Usage:
    ./verify_vertex_access.py                          # uses GOOGLE_CLOUD_PROJECT or the default below
    ./verify_vertex_access.py --project som-nero-phi-jonc101

Sends only a generic, non-PHI prompt. Prints OK/FAIL per model so you can see which
families your project + credentials can reach before running the pipeline.

Notes from the Stanford Vertex reference:
  - GA / BAA-covered models only for PHI (no -preview slugs; no OpenAI/GPT).
  - Gemini -> google.genai (us-central1); Claude -> anthropic.AnthropicVertex
    (Opus=global, Sonnet/Haiku=us-east5); Llama -> OpenAI-compatible (us-east5).
"""

import argparse
import os

PROMPT = "In one sentence, what is a urinary tract infection?"


def test_gemini(project, model, location="us-central1", thinking_budget=None, max_tokens=1024):
    from google import genai
    from google.genai import types
    client = genai.Client(vertexai=True, project=project, location=location)
    cfg_kwargs = {"max_output_tokens": max_tokens}
    # 2.5 Flash accepts thinking_budget=0; 2.5 Pro REJECTS 0 (HTTP 400) -> leave it unset and
    # give a generous token budget so thinking doesn't starve the visible output.
    if thinking_budget is not None:
        cfg_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)
    resp = client.models.generate_content(
        model=model,
        contents=PROMPT,
        config=types.GenerateContentConfig(**cfg_kwargs),
    )
    return (resp.text or "").strip()


def test_claude(project, model, region):
    from anthropic import AnthropicVertex
    client = AnthropicVertex(project_id=project, region=region)
    msg = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return msg.content[0].text.strip()


def test_llama(project, model, location="us-east5"):
    import google.auth
    import google.auth.transport.requests
    from openai import OpenAI
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    client = OpenAI(
        base_url=(f"https://{location}-aiplatform.googleapis.com/v1beta1/"
                  f"projects/{project}/locations/{location}/endpoints/openapi"),
        api_key=creds.token,
    )
    resp = client.chat.completions.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return resp.choices[0].message.content.strip()


def main():
    ap = argparse.ArgumentParser(description="Smoke-test Vertex AI model access (uses your ADC)")
    ap.add_argument("--project",
                    default=os.getenv("VERTEX_PROJECT", "som-nero-phi-jonc101-secure"),
                    help="GCP project ID (default: VERTEX_PROJECT or som-nero-phi-jonc101-secure)")
    args = ap.parse_args()
    p = args.project

    print(f"Project : {p}")
    print(f"Prompt  : {PROMPT}\n")

    tests = [
        ("Gemini 2.5 Pro",    lambda: test_gemini(p, "gemini-2.5-pro", max_tokens=2048)),
        ("Gemini 2.5 Flash",  lambda: test_gemini(p, "gemini-2.5-flash", thinking_budget=0, max_tokens=512)),
        ("Claude Sonnet 4.6", lambda: test_claude(p, "claude-sonnet-4-6@default", "us-east5")),
        ("Claude Opus 4.7",   lambda: test_claude(p, "claude-opus-4-7@default", "global")),
        ("Llama 4 Maverick",  lambda: test_llama(p, "meta/llama-4-maverick-17b-128e-instruct-maas")),
    ]

    ok = 0
    for name, fn in tests:
        try:
            out = fn()
            print(f"[OK]   {name:20s}: {out[:90]}")
            ok += 1
        except Exception as e:
            print(f"[FAIL] {name:20s}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(tests)} models reachable.")


if __name__ == "__main__":
    main()
