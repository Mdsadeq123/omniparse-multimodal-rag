# OmniParse — Multimodal RAG Engine

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-green)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM_Gateway-black)

**OmniParse** is a local-first, highly optimized Multimodal Retrieval-Augmented Generation (RAG) application. It allows users to ingest, index, and semantically search across unstructured documents (PDF, DOCX, TXT, MD) and complex images (PNG, JPG). Built with strict source grounding, it ensures all LLM responses are accurately attributed to the original uploaded files.

---

## 🚀 Key Engineering Highlights

This project was built with a focus on production-ready robust engineering patterns and optimal user experience:

- **Smart Multimodal Ingestion & Deduplication:** Handles both text and image formats seamlessly. Integrates **SHA-256 cryptographic hashing** to prevent redundant processing and save vector database storage when duplicate files are uploaded.
- **Advanced Spatial OCR Pipeline:** Leverages **EasyOCR** combined with spatial Y-coordinate bounding-box alignment to preserve tabular data and multi-column layouts, preventing data flattening and drastically improving vector embedding similarity scores.
- **Vision-Enhanced Context:** Uses cutting-edge Vision-Language Models (VLMs) via OpenRouter to generate rich, descriptive metadata captions for all ingested images, enriching the vector index.
- **Resilient API Architecture:** Powered by **FastAPI** with robust error handling, catching upstream 429/502 API rate limits and translating them into clean, user-friendly frontend payloads rather than raw tracebacks.
- **Intuitive UI with Custom Citation Parsing:** A vanilla JS/CSS frontend featuring interactive source snippet expansion (`-webkit-line-clamp`), real-time status updates, and custom regex parsers that convert raw LLM citation outputs into clean, responsive UI badges.

---

## 🛠️ Architecture & Tech Stack

- **Backend Framework:** FastAPI, Uvicorn
- **AI Orchestration:** LangChain
- **Vector Database:** ChromaDB (Persistent local storage)
- **Optical Character Recognition (OCR):** EasyOCR (PyTorch)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **LLM Provider:** OpenRouter (NVIDIA Nemotron ecosystem)

### Default Models
| Role | Model ID |
| :--- | :--- |
| **Chat Generation** | `nvidia/nemotron-3-super-120b-a12b:free` |
| **Vector Embeddings** | `nvidia/llama-nemotron-embed-vl-1b-v2:free` |
| **Vision Captions** | `nvidia/nemotron-nano-12b-v2-vl:free` |

---

## ⚙️ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- An [OpenRouter API Key](https://openrouter.ai/)

### 2. Environment Setup

```bash
# Clone repository
git clone https://github.com/Mdsadeq123/omniparse-multimodal-rag.git
cd omniparse-multimodal-rag

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Rename `.env.example` to `.env` and insert your API key:
```env
OPENROUTER_API_KEY="sk-or-v1-..."
```

### 4. Run the Application
Start the Uvicorn server:
```bash
python run.py
```
*Navigate to `http://localhost:8000` in your browser to interact with the application!*

---

## 📁 Project Structure

```text
omniparse-multimodal-rag/
├── app/
│   ├── api/            # FastAPI route definitions (chat, documents, ingest)
│   ├── models/         # Pydantic schemas for request/response validation
│   └── services/       # Core business logic (RAG, OCR, Chunking, ChromaDB)
├── static/             # Frontend assets (Vanilla JS, CSS, index.html)
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
└── .env                # Environment variables
```
