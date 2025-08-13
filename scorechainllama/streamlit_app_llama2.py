
import streamlit as st
import os, requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-2-7b-chat-hf")
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models")
HF_MAX_NEW_TOKENS = int(float(os.getenv("HF_MAX_NEW_TOKENS", "700")))
HF_TEMPERATURE = float(os.getenv("HF_TEMPERATURE", "0.2"))

st.set_page_config(page_title="Assignment 2 – Llama 2 Updater", layout="wide")
st.title("🦙 Assignment 2 – Llama 2 Updater")

if not HF_TOKEN:
    st.error("Missing HF_TOKEN. Set it in .env.")
    st.stop()

def call_hf(system: str, user: str) -> str:
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
    try:
        r.raise_for_status()
        data = r.json()
        return data[0]["generated_text"]
    except Exception:
        return str(r.text)

tab1, tab2, tab3 = st.tabs(["Update Planner", "Fraud SQL", "Docstrings"])

with tab1:
    st.subheader("Project Update Planner")
    ctx = st.text_area("Project context", placeholder="Domain, users, goals, KPIs, tech stack...", height=140)
    readme = st.text_area("Current README (optional)", height=160)
    backlog = st.text_area("Backlog items (one per line)", height=120)
    focus = st.multiselect("Focus areas", ["docs","testing","performance","sql","security","ux","tracking"], default=["docs","testing","sql"])
    fmt = st.selectbox("Output format", ["json","markdown"], index=0)
    if st.button("Generate plan"):
        from templates.update_plan import SYSTEM_PROMPT as SYS, USER_TEMPLATE
        user = USER_TEMPLATE.format(
            project_context=ctx,
            current_readme=readme or "N/A",
            backlog="\\n".join(f"- {b}" for b in (backlog.splitlines() if backlog else [])),
            focus_areas=", ".join(focus),
            output_format=fmt,
        )
        out = call_hf(SYS, user)
        st.text_area("Output", out, height=360)

with tab2:
    st.subheader("Fraud/Transactions SQL Generator")
    schema = st.text_area("Schema / DDL", placeholder="Tables, columns, PK/FK, sample rows...", height=200)
    dialect = st.selectbox("SQL Dialect", ["postgres","mysql","mssql","bigquery","snowflake"])
    n = st.slider("How many queries?", 1, 50, 10)
    objective = st.text_input("Objective", "Generate SQL to detect fraudulent transactions across scenarios.")
    if st.button("Generate SQL"):
        from templates.fraud_sql import SYSTEM_PROMPT as SYS, USER_TEMPLATE
        user = USER_TEMPLATE.format(schema=schema, objective=objective, n=n, dialect=dialect)
        out = call_hf(SYS, user)
        st.text_area("SQL Output", out, height=360)

with tab3:
    st.subheader("Docstrings & Comments")
    code = st.text_area("Paste code", height=220)
    style = st.selectbox("Docstring style", ["google","numpy","sphinx"])
    level = st.selectbox("Detail level", ["concise","detailed"])
    if st.button("Propose docstrings"):
        from templates.docstrings import SYSTEM_PROMPT as SYS, USER_TEMPLATE
        user = USER_TEMPLATE.format(code=code, style=style, level=level)
        out = call_hf(SYS, user)
        st.text_area("Docstrings", out, height=360)
