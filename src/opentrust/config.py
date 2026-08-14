"""Runtime configuration, sourced from environment variables."""
import os
from dataclasses import dataclass, field


def _split_csv(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass
class Settings:
    cors_origins: list[str] = field(
        default_factory=lambda: _split_csv(os.environ.get("OPENTRUST_CORS_ORIGINS", "*"))
    )
    host: str = field(default_factory=lambda: os.environ.get("OPENTRUST_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.environ.get("OPENTRUST_PORT", "8000")))
    log_level: str = field(default_factory=lambda: os.environ.get("OPENTRUST_LOG_LEVEL", "info"))


settings = Settings()
