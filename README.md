# OmniParse — Multimedia RAG Summarization Engine

Local-first web app to upload **documents** (PDF, DOCX, TXT, MD) and **images** (PNG, JPG, etc.), index them with Chroma + OpenRouter embeddings, and **chat** with RAG-grounded answers.

**Default models (NVIDIA via OpenRouter):**

| Role | Model ID |
|------|----------|
| Chat | `nvidia/nemotron-3-super-120b-a12b:free` |
| Embeddings | `nvidia/llama-nemotron-embed-vl-1b-v2:free` |
| Vision captions | `nvidia/nemotron-nano-12b-v2-vl:free` |

Use your normal **OpenRouter API key** — no separate NVIDIA key required.

## Prerequisites

- Python 3.11+
- [OpenRouter](https://openrouter.ai/) API key
- ~2 GB disk space for EasyOCR models (downloaded on first image upload)

## Setup

```bash
cd rag-multimedia
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Edit `.env` and set `OPENROUTER_API_KEY`.

Optional: enable vision captions for sparse OCR:

```env
VISION_CAPTION_ENABLED=true
```

## Run

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ingest` | Upload and index files (multipart `files`) |
| POST | `/api/chat` | RAG chat `{ "message": "...", "top_k": 5 }` |
| GET | `/api/documents` | List indexed documents |
| DELETE | `/api/documents/{doc_id}` | Remove document and chunks |
| GET | `/health` | Health check |

## Manual test checklist

1. **Health** — `GET /health` returns `api_key_set: true` after setting `.env`.
2. **Text file** — Upload a `.txt` with a unique fact; ask about that fact; answer should cite the file.
3. **PDF** — Upload a PDF; ask a question answerable only from its content.
4. **Image OCR** — Upload a screenshot with visible text; ask about text in the image.
5. **Persistence** — Restart the server; previously indexed docs still appear in the list and chat works.
6. **Delete** — Delete a document; it disappears from the list and is no longer retrieved in chat.

## Project structure

```
omniparse/  (repo folder may be rag-multimedia)
├── app/           # FastAPI backend
├── static/        # Web UI
├── data/uploads/  # Raw uploads (gitignored)
├── data/chroma/   # Vector store (gitignored)
└── requirements.txt
```

## Configuration

See `.env.example` for all options:

- `CHAT_MODEL` — default `nvidia/nemotron-3-super-120b-a12b:free` ([Nemotron 3 Super](https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free), 1M context)
- `EMBEDDING_MODEL` — default `nvidia/llama-nemotron-embed-vl-1b-v2:free` (multimodal retrieval)
- `VISION_MODEL` — default `nvidia/nemotron-nano-12b-v2-vl:free` (image captions when enabled)
- Paid Nemotron 3 Super (no rate limits): `nvidia/nemotron-3-super-120b-a12b`
- `MAX_UPLOAD_MB` — max file size (default: 25)
- `TOP_K` — chunks retrieved per question (default: 5)

## Notes

- First image ingest downloads EasyOCR weights; this can take several minutes.
- MVP runs on localhost without authentication — not for production exposure.
- Re-uploading the same file creates a new `doc_id`; delete old entries manually if needed.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `OPENROUTER_API_KEY is not set` | Create `.env` from `.env.example` |
| Embedding/chat 401 | Verify OpenRouter API key and credits |
| Model not found | Check model IDs on [openrouter.ai/nvidia](https://openrouter.ai/nvidia) |
| Free tier slow / logged | Use paid `nvidia/nemotron-3-super-120b-a12b` or accept free-tier limits |
| `No embedding data received` | Fixed via Nemotron VL input format; restart server; if persists, delete `data/chroma/` and re-upload |
| OCR very slow | Expected on CPU; first run also downloads models |
| Empty PDF chunks | PDF may be scanned images only — try uploading as PNG with OCR |
