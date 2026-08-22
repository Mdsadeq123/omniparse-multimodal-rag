import hashlib
import re
import uuid
from pathlib import Path

from fastapi import UploadFile
from langchain_core.documents import Document

from app.config import settings
from app.services.chunking import chunk_documents
from app.services.image_processor import process_image
from app.services.loaders import load_document
from app.services.vectorstore import add_documents, delete_by_doc_id, find_by_hash

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def sanitize_filename(name: str) -> str:
    name = Path(name).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name or "upload"


def is_image(ext: str) -> bool:
    return ext.lower() in IMAGE_EXTENSIONS


async def ingest_file(file: UploadFile) -> dict:
    if not file.filename:
        raise ValueError("Filename is required")

    filename = sanitize_filename(file.filename)
    ext = Path(filename).suffix.lower()

    if ext not in settings.allowed_extensions:
        raise ValueError(f"File type not allowed: {ext}")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise ValueError(f"File exceeds {settings.max_upload_mb} MB limit")

    file_hash = hashlib.sha256(content).hexdigest()
    existing_doc_id = find_by_hash(file_hash)
    if existing_doc_id:
        return {
            "doc_id": existing_doc_id,
            "filename": filename,
            "chunks_added": 0,
            "status": "already indexed",
        }

    doc_id = str(uuid.uuid4())
    doc_dir = settings.uploads_path / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)
    file_path = doc_dir / filename
    file_path.write_bytes(content)

    if is_image(ext):
        raw_docs = process_image(file_path, doc_id, filename)
    else:
        raw_docs = load_document(file_path, doc_id, filename)

    if not raw_docs:
        raise ValueError("No text could be extracted from the file")

    chunks = chunk_documents(raw_docs)
    if not chunks:
        raise ValueError("No chunks produced from the file")
        
    for chunk in chunks:
        if chunk.metadata is None:
            chunk.metadata = {}
        chunk.metadata["file_hash"] = file_hash

    delete_by_doc_id(doc_id)

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    add_documents(chunks, ids)

    return {
        "doc_id": doc_id,
        "filename": filename,
        "chunks_added": len(chunks),
        "status": "indexed",
    }
