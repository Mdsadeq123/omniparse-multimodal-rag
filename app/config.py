from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "http://localhost:8000"
    openrouter_app_title: str = "OmniParse"

    # NVIDIA Nemotron via OpenRouter (https://openrouter.ai/nvidia)
    chat_model: str = "nvidia/nemotron-3-super-120b-a12b:free"
    embedding_model: str = "nvidia/llama-nemotron-embed-vl-1b-v2:free"
    vision_model: str = "nvidia/nemotron-nano-12b-v2-vl:free"

    chroma_persist_dir: str = "./data/chroma"
    upload_dir: str = "./data/uploads"
    top_k: int = 5
    max_upload_mb: int = 25
    vision_caption_enabled: bool = False

    collection_name: str = "multimedia_rag"

    allowed_extensions: set[str] = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
        ".markdown",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".bmp",
    }

    @property
    def chroma_path(self) -> Path:
        p = Path(self.chroma_persist_dir)
        return p if p.is_absolute() else BASE_DIR / p

    @property
    def uploads_path(self) -> Path:
        p = Path(self.upload_dir)
        return p if p.is_absolute() else BASE_DIR / p

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
