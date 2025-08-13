
import os, requests
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-2-7b-chat-hf")
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models")
HF_MAX_NEW_TOKENS = int(float(os.getenv("HF_MAX_NEW_TOKENS", "700")))
HF_TEMPERATURE = float(os.getenv("HF_TEMPERATURE", "0.2"))

if not HF_TOKEN:
    raise RuntimeError("Missing HF_TOKEN. Set it in your environment or .env file.")

def call_hf_chat(system: str, user: str) -> str:
    # Compose a single prompt; many chat-optimized models accept this as plain text
    prompt = f"<<SYS>>{system}<</SYS>>\n\nUser: {user}\nAssistant:"
    url = f"{HF_API_URL.rstrip('/')}/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": HF_MAX_NEW_TOKENS,
            "temperature": HF_TEMPERATURE,
            "return_full_text": False
        }
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    # HF returns a list with {'generated_text': ...} for text-generation
    try:
        return data[0]["generated_text"]
    except Exception:
        return str(data)

app = FastAPI(title="Assignment 2 – Llama 2 Updater API", version="1.0.0")

class UpdateRequest(BaseModel):
    project_context: str = Field(..., description="Short description of your project (domain, goals, users).")
    current_readme: Optional[str] = Field(None, description="Existing README text, optional.")
    backlog: Optional[List[str]] = Field(None, description="Bullet list of pending tasks / issues.")
    focus_areas: Optional[List[str]] = Field(default_factory=lambda: ["docs","testing","performance","sql","security"])
    output_format: str = Field("json", description="json or markdown")

class FraudSQLRequest(BaseModel):
    schema: str = Field(..., description="DDL or description of tables/columns/keys.")
    objective: str = Field("Generate SQL to detect fraudulent transactions across scenarios.")
    n_queries: int = Field(10, ge=1, le=50)
    dialect: str = Field("postgres", description="postgres|mysql|mssql|bigquery|snowflake")

class DocstringsRequest(BaseModel):
    code: str = Field(..., description="Source code to document.")
    style: str = Field("google", description="google|numpy|sphinx")
    level: str = Field("concise", description="concise|detailed")

@app.post("/update")
def generate_update(req: UpdateRequest) -> Dict[str, Any]:
    from templates.update_plan import SYSTEM_PROMPT as SYS, USER_TEMPLATE
    user = USER_TEMPLATE.format(
        project_context=req.project_context,
        current_readme=req.current_readme or "N/A",
        backlog="\n".join(f"- {b}" for b in (req.backlog or [])),
        focus_areas=", ".join(req.focus_areas or []),
        output_format=req.output_format,
    )
    out = call_hf_chat(SYS, user)
    return {"result": out}

@app.post("/fraud-sql")
def fraud_sql(req: FraudSQLRequest) -> Dict[str, Any]:
    from templates.fraud_sql import SYSTEM_PROMPT as SYS, USER_TEMPLATE
    user = USER_TEMPLATE.format(
        schema=req.schema,
        objective=req.objective,
        n=req.n_queries,
        dialect=req.dialect,
    )
    out = call_hf_chat(SYS, user)
    return {"result": out}

@app.post("/docstrings")
def docstrings(req: DocstringsRequest) -> Dict[str, Any]:
    from templates.docstrings import SYSTEM_PROMPT as SYS, USER_TEMPLATE
    user = USER_TEMPLATE.format(code=req.code, style=req.style, level=req.level)
    out = call_hf_chat(SYS, user)
    return {"result": out}
