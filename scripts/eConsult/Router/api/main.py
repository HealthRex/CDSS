from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import json
import sys
from pathlib import Path
import requests
from typing import Optional

# Add PROJECT ROOT to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
print("DEBUG: project root =", PROJECT_ROOT)

from utils.config import Config


app = FastAPI(title="SAGE Router", version="1.0")
cfg = Config()

# Global cache variables
specialty_conditions = {}
templates_text = ""
cache_metadata = {}

# Load cache on startup
@app.on_event("startup")
async def load_cache():
    global specialty_conditions, templates_text, cache_metadata
    
    print("🔄 Loading routing cache...")
    
    # Load specialty-condition mapping
    mapping_path = cfg.results_dir / "specialty_condition_mapping.json"
    if mapping_path.exists():
        with open(mapping_path, "r") as f:
            specialty_conditions = json.load(f)
        print(f"✅ Loaded {len(specialty_conditions)} specialties")
    
    # Load cache content
    cache_path = cfg.results_dir / "cache_content.txt"
    if cache_path.exists():
        with open(cache_path, "r") as f:
            cache_content = f.read()
            # Extract templates section
            templates_section = cache_content.split("=== SPECIALTY MAPPINGS ===")[0]
            templates_text = templates_section.replace("=== TEMPLATES ===\n", "").strip()
        print(f"✅ Loaded templates cache")
    
    # Load cache metadata
    metadata_path = cfg.results_dir / "cache_metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            cache_metadata = json.load(f)
        print(f"✅ Cache metadata: hash={cache_metadata.get('content_hash')}")

# Routing function 
def route_question(question: str):
    """Route a clinical question to specialties and conditions"""
    
    # Build specialty mapping text
    specialty_mapping_text = ""
    for specialty, conditions in specialty_conditions.items():
        specialty_mapping_text += f"\n{specialty}: {', '.join(conditions[:10])}..."
    
    # System prompt
    system_prompt = f"""You are a clinical reasoning assistant.
Given a patient's eConsult question, determine:
(1) The top 3 most appropriate specialties (ranked by relevance).
(2) The top 5 most relevant template conditions (ranked by relevance).

CRITICAL CONSTRAINT: All 5 conditions MUST be from the TOP specialty you choose.

Note: For the following conditions, consider these specialties:
- Vertigo: Both ENT-Otolaryngology and Neurology are valid
- Tinnitus: Both ENT-Otolaryngology and Neurology are valid
- Sinusitis: ENT-Otolaryngology is primary, Internal Medicine may be relevant

Available specialty-condition mappings:
{specialty_mapping_text}

Return your answer strictly in JSON format:
{{
    "specialties": ["specialty1", "specialty2", "specialty3"],
    "conditions": ["condition1", "condition2", "condition3", "condition4", "condition5"]
}}"""

    user_prompt = f"Clinical Question:\n{question}\n\nAvailable Templates:\n{templates_text}"
    
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": cfg.securegpt_api_key,
    }
    
    payload = {
        "model": cfg.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    }
    
    try:
        response = requests.post(cfg.securegpt_url, headers=headers, json=payload)
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]["content"]
        result = json.loads(message)
        
        specialties = result.get("specialties", [])[:3]
        conditions = result.get("conditions", [])[:5]
        
        # Pad with empty strings if needed
        while len(specialties) < 3:
            specialties.append("")
        while len(conditions) < 5:
            conditions.append("")
            
        return {
            "specialties": specialties,
            "conditions": conditions,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            "specialties": ["Error", "", ""],
            "conditions": ["Error processing request", "", "", "", ""],
            "status": "error",
            "error": str(e)
        }

# HTML UI with better styling
@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
    <html>
    <head>
        <title>SAGE Router</title>
        <style>
            :root {{
                --bg: #0f172a;
                --card-bg: #ffffff;
                --accent: #2563eb;
                --accent-soft: #dbeafe;
                --text-main: #0f172a;
                --text-muted: #6b7280;
                --error: #b91c1c;
            }}
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
                background: radial-gradient(circle at top left, #1e293b, #020617);
                color: var(--text-main);
            }}
            .page {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }}
            .card {{
                width: 100%;
                max-width: 960px;
                background: var(--card-bg);
                border-radius: 18px;
                box-shadow:
                    0 20px 25px -5px rgba(15,23,42,0.25),
                    0 8px 10px -6px rgba(15,23,42,0.20);
                padding: 24px 32px 28px;
            }}
            .header {{
                display: flex;
                align-items: center;
                margin-bottom: 16px;
            }}
            .logo-pill {{
                width: 40px;
                height: 40px;
                border-radius: 999px;
                background: linear-gradient(135deg, #22c55e, #0ea5e9);
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                color: white;
                font-size: 20px;
            }}
            h1 {{
                font-size: 24px;
                margin: 0;
                color: var(--text-main);
            }}
            .subtitle {{
                margin-top: 4px;
                font-size: 14px;
                color: var(--text-muted);
            }}
            .info-bar {{
                margin-top: 16px;
                background: var(--accent-soft);
                border-radius: 10px;
                padding: 10px 12px;
                font-size: 13px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #1e40af;
            }}
            .pill {{
                padding: 4px 10px;
                border-radius: 999px;
                background: white;
                border: 1px solid #bfdbfe;
                font-size: 12px;
            }}
            .label {{
                font-size: 14px;
                font-weight: 600;
                margin-top: 20px;
                margin-bottom: 8px;
                color: var(--text-main);
            }}
            textarea {{
                width: 100%;
                min-height: 220px;
                resize: vertical;
                padding: 12px 14px;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                font-size: 14px;
                line-height: 1.5;
                font-family: inherit;
                outline: none;
                transition: border-color 0.15s ease, box-shadow 0.15s ease;
            }}
            textarea:focus {{
                border-color: var(--accent);
                box-shadow: 0 0 0 1px var(--accent-soft);
            }}
            .hint {{
                margin-top: 6px;
                font-size: 12px;
                color: var(--text-muted);
            }}
            .actions {{
                margin-top: 18px;
                display: flex;
                justify-content: flex-end;
            }}
            button {{
                border: none;
                border-radius: 999px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: linear-gradient(135deg, #2563eb, #4f46e5);
                color: white;
                box-shadow: 0 10px 18px -8px rgba(37,99,235,0.7);
                transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
            }}
            button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 16px 25px -12px rgba(37,99,235,0.85);
                filter: brightness(1.03);
            }}
            button:active {{
                transform: translateY(0);
                box-shadow: 0 8px 14px -8px rgba(37,99,235,0.7);
            }}
            .rocket {{
                font-size: 16px;
            }}
            .footer {{
                margin-top: 12px;
                font-size: 11px;
                color: rgba(148,163,184,0.95);
                text-align: right;
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <div class="card">
                <div class="header">
                    <div class="logo-pill">🩺</div>
                    <div>
                        <h1>SAGE Router – Clinical Question Routing</h1>
                        <div class="subtitle">
                            Paste a clinician’s eConsult question and preview where SAGE would send it.
                        </div>
                    </div>
                </div>

                <div class="info-bar">
                    <div><strong>Instructions:</strong> Enter a clinical question to route it to appropriate specialties and template conditions.</div>
                    <div class="pill">Cache loaded: {len(specialty_conditions)} specialties</div>
                </div>

                <div class="label">Clinical question</div>
                <form action="/route" method="post">
                    <textarea name="question" placeholder="Example: 68-year-old male with history of asthma reporting persistent shortness of breath with exertion and dry cough..."></textarea>
                    <div class="hint">
                        No PHI is stored. The router only uses this text to select specialties and condition templates.
                    </div>

                    <div class="actions">
                        <button type="submit">
                            <span class="rocket">🚀</span>
                            <span>Route Question</span>
                        </button>
                    </div>
                </form>

                <div class="footer">
                    Prototype SAGE router · Local cache hash: {cache_metadata.get("content_hash", "n/a")}
                </div>
            </div>
        </div>
    </body>
    </html>
    """


# Route endpoint (returns HTML)
@app.post("/route", response_class=HTMLResponse)
async def route(request: Request):
    form = await request.form()
    question = form.get("question")

    if not question:
        return """
        <html><body><h3>Error: No question provided</h3><a href="/">Go back</a></body></html>
        """

    # Call routing function
    result = route_question(question)

    specialties_html = "<ol>" + "".join(
        [f"<li>{s}</li>" for s in result["specialties"] if s]
    ) + "</ol>"
    conditions_html = "<ol>" + "".join(
        [f"<li>{c}</li>" for c in result["conditions"] if c]
    ) + "</ol>"

    status_ok = result["status"] == "success"
    status_text = "SUCCESS" if status_ok else "ERROR"
    status_color = "#16a34a" if status_ok else "#b91c1c"

    error_box = ""
    if not status_ok and result.get("error"):
        error_box = f"""
        <div class="card error-card">
            <strong>Details:</strong>
            <pre>{result["error"]}</pre>
        </div>
        """

    top_specialty = result["specialties"][0] if result["specialties"] else "N/A"

    return f"""
    <html>
    <head>
        <title>SAGE Router – Results</title>
        <style>
            :root {{
                --bg: #0f172a;
                --card-bg: #ffffff;
                --accent: #2563eb;
                --text-main: #0f172a;
                --text-muted: #6b7280;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
                background: radial-gradient(circle at top left, #1e293b, #020617);
                color: var(--text-main);
            }}
            .page {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }}
            .container {{
                width: 100%;
                max-width: 960px;
            }}
            .card {{
                background: var(--card-bg);
                border-radius: 18px;
                box-shadow:
                    0 20px 25px -5px rgba(15,23,42,0.25),
                    0 8px 10px -6px rgba(15,23,42,0.20);
                padding: 20px 24px;
                margin-bottom: 16px;
            }}
            .header-row {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 4px;
            }}
            .title-icon {{
                font-size: 22px;
            }}
            h2 {{
                margin: 0;
                font-size: 22px;
            }}
            .status {{
                font-size: 14px;
                font-weight: 700;
                margin-bottom: 12px;
                color: {status_color};
            }}
            .question-box {{
                background: #f3f4f6;
                border-radius: 10px;
                padding: 12px 14px;
                font-size: 14px;
                line-height: 1.5;
            }}
            .section-title {{
                font-size: 15px;
                font-weight: 600;
                margin-bottom: 6px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .section-subtitle {{
                font-size: 12px;
                color: var(--text-muted);
                margin-bottom: 6px;
            }}
            ol {{
                margin: 4px 0 0 20px;
                padding: 0;
                line-height: 1.6;
                font-size: 14px;
            }}
            .layout {{
                display: grid;
                grid-template-columns: minmax(0,1.1fr) minmax(0,1fr);
                gap: 16px;
            }}
            .pill-link {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                text-decoration: none;
                color: var(--accent);
                margin-top: 6px;
            }}
            .pill-link span.icon {{ font-size: 15px; }}
            .back {{
                margin-top: 8px;
                text-align: left;
            }}
            .back a {{
                text-decoration: none;
                color: var(--accent);
                font-size: 13px;
            }}
            .error-card {{
                border-left: 4px solid #ef4444;
                background: #fef2f2;
                font-size: 12px;
                color: #7f1d1d;
            }}
            pre {{
                margin: 8px 0 0;
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <div class="container">

                <div class="card">
                    <div class="header-row">
                        <div class="title-icon">🔍</div>
                        <h2>Routing Results</h2>
                    </div>
                    <div class="status">Status: {status_text}</div>
                    <div class="question-box">
                        <strong>Question:</strong><br>
                        {question}
                    </div>
                    <div class="back">
                        <a href="/">← Route another question</a>
                    </div>
                </div>

                <div class="layout">
                    <div class="card">
                        <div class="section-title">
                            🏥 Top Specialties (Ranked)
                        </div>
                        <div class="section-subtitle">
                            These are the specialties the router believes are the best fit for this question.
                        </div>
                        {specialties_html}
                    </div>

                    <div class="card">
                        <div class="section-title">
                            📋 Top Conditions from {top_specialty}
                        </div>
                        <div class="section-subtitle">
                            Condition templates within the top specialty that best match this question.
                        </div>
                        {conditions_html}
                    </div>
                </div>

                {error_box}

            </div>
        </div>
    </body>
    </html>
    """


# API endpoint (returns JSON)
class QuestionRequest(BaseModel):
    question: str

@app.post("/api/route")
async def api_route(request: QuestionRequest):
    result = route_question(request.question)
    return JSONResponse(content=result)

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "cache_loaded": len(specialty_conditions) > 0,
        "specialties_count": len(specialty_conditions),
        "cache_hash": cache_metadata.get("content_hash", "unknown")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
