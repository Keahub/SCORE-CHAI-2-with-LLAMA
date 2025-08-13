import argparse, os, pathlib, requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-2-7b-chat-hf")
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models")
HF_MAX_NEW_TOKENS = int(float(os.getenv("HF_MAX_NEW_TOKENS", "700")))
HF_TEMPERATURE = float(os.getenv("HF_TEMPERATURE", "0.2"))

if not HF_TOKEN:
    raise SystemExit("Missing HF_TOKEN. Set it in .env")

SYSTEM = "You are a pragmatic code reviewer and product lead. Return markdown only."

PROMPT = (
    "You will scan a project and produce:\n"
    "1) README improvements\n"
    "2) Test gaps\n"
    "3) Security/PII risks\n"
    "4) SQL/fraud analytics ideas (if applicable)\n"
    "5) A prioritized, ticket-sized TODO list with acceptance criteria\n\n"
    "Project Snapshot (filenames and excerpts):\n{snapshot}\n"
)

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
    r.raise_for_status()
    data = r.json()
    try:
        return data[0]["generated_text"]
    except Exception:
        return str(data)

def snapshot_path(path: str, max_files=40, max_chars=8000) -> str:
    root = pathlib.Path(path)
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".py",".ipynb",".md",".sql",".yml",".yaml",".json",".toml",".ini"}:
            files.append(p)
        if len(files) >= max_files:
            break
    pieces = []
    for f in files:
        try:
            txt = f.read_text(errors="ignore")
        except Exception:
            continue
        pieces.append(f"## {f.relative_to(root)}\n{txt[:400]}")
    snap = "\n\n".join(pieces)
    return snap[:max_chars]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Path to existing project")
    ap.add_argument("--outfile", default="AI_UPDATE_NOTES_LLAMA2.md", help="Output file path")
    ap.add_argument("--max-files", type=int, default=40)
    args = ap.parse_args()

    snap = snapshot_path(args.path, max_files=args.max_files)
    user = PROMPT.format(snapshot=snap)
    out = call_hf(SYSTEM, user)
    pathlib.Path(args.outfile).write_text(out, encoding="utf-8")
    print(f"Wrote {args.outfile}")

if __name__ == "__main__":
    main()
