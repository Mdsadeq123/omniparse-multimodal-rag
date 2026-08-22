from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from app.config import settings
from app.models.schemas import ChatResponse, SourceCitation
from app.services.openrouter import get_openrouter_client_kwargs
from app.services.vectorstore import get_vectorstore

SYSTEM_PROMPT = """You answer only from the context below. If the answer is not in the context, say you don't know.
Do NOT use numerical citations like [1] or [2]. Cite sources explicitly using the format [filename, page/section] when possible. Be concise and accurate."""


def _format_context(docs: list[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata or {}
        source = meta.get("source", "unknown")
        page = meta.get("page", "")
        doc_type = meta.get("type", "document")
        header = f"[{i}] {source}"
        if page:
            header += f" (page {page})"
        header += f" [{doc_type}]"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def chat(message: str, top_k: int | None = None) -> ChatResponse:
    k = top_k or settings.top_k
    store = get_vectorstore()
    results = store.similarity_search_with_score(message, k=k)

    if not results:
        return ChatResponse(
            answer="No indexed documents found. Upload files first.",
            sources=[],
        )

    docs = [doc for doc, _ in results]
    context = _format_context(docs)

    llm = ChatOpenAI(
        model=settings.chat_model,
        temperature=0.2,
        **get_openrouter_client_kwargs(),
    )

    try:
        response = llm.invoke(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    f"Context:\n{context}\n\nQuestion:\n{message}",
                ),
            ]
        )
    except Exception as e:
        error_str = str(e)
        if "502" in error_str or "429" in error_str:
            raise ValueError("Service is temporarily busy. Please try again in a few seconds.") from e
        raise e

    sources: list[SourceCitation] = []
    for doc, score in results:
        meta = doc.metadata or {}
        snippet = doc.page_content[:300]
        if len(doc.page_content) > 300:
            snippet += "..."
        sources.append(
            SourceCitation(
                file=meta.get("source", "unknown"),
                snippet=snippet,
                score=round(float(score), 4) if score is not None else None,
                page=meta.get("page"),
                doc_type=meta.get("type"),
            )
        )

    answer = response.content if hasattr(response, "content") else str(response)
    return ChatResponse(answer=answer, sources=sources)
