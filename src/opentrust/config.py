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


settings = Settings()
