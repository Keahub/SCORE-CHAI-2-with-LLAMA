# Assignment 2 – Llama 2 LLM Add‑On (Hugging Face Inference API)

This add‑on plugs into your scorechain2 project to perform **project‑based updates** using **Llama 2** via the **Hugging Face Inference API**.
It includes:
- **FastAPI** service with endpoints: `/update`, `/fraud-sql`, `/docstrings`
- **Streamlit** UI for quick testing
- **CLI** (`tools/llama2_update.py`) to scan a codebase and generate `AI_UPDATE_NOTES.md`
- **Prompt templates** in `templates/` you can customize

> Default model: `meta-llama/Llama-2-7b-chat-hf` (you must accept the model license on Hugging Face).

## Quickstart

1) **Install deps**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your HF token
```

2) **Run the API**
```bash
uvicorn app_fastapi_llama2:app --host 0.0.0.0 --port 8001 --reload
# Docs: http://localhost:8001/docs
```

3) **Run the Streamlit UI**
```bash
streamlit run streamlit_app_llama2.py
```

4) **Use the CLI on your existing Assignment 2 project**
```bash
python tools/llama2_update.py --path "../zeru finance assignment_2 project folder"   --outfile "../AI_UPDATE_NOTES_LLAMA2.md"
```

## Configure

Set these in `.env` (or environment):
```
HF_TOKEN=hf_xxx_your_token_here
HF_MODEL=meta-llama/Llama-2-7b-chat-hf
HF_API_URL=https://api-inference.huggingface.co/models
HF_MAX_NEW_TOKENS=700
HF_TEMPERATURE=0.2
```

> Tip: If you hit the **loading** state on first call, the Inference API may start the model container; just retry after a moment.

## Endpoints

- `POST /update` – produce a sprint‑ready update plan (JSON/Markdown)
- `POST /fraud-sql` – generate diverse fraud/transactions SQL ideas (dialect‑aware)
- `POST /docstrings` – propose docstrings/comments for pasted code

## Safe use

This tool **does not auto‑modify** your code. It proposes plans, SQL, docstrings, and notes. Review outputs before committing.

