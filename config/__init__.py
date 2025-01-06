from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from config import crypt
from config._app import AppSettings, DatabaseSettings, ServerSettings, ViteSettings
from config._base import get_config_val, get_env

__all__ = ("AppSettings", "DatabaseSettings", "ServerSettings", "Settings", "ViteSettings", "crypt", "get_config_val", "get_env", "get_settings")


@dataclass
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    vite: ViteSettings = field(default_factory=ViteSettings)

    @classmethod
    @lru_cache(maxsize=1, typed=True)
    def from_env(cls, dotenv_filename: str = ".env") -> Settings:
        from litestar.cli._utils import console

        env_file = Path(f"{os.curdir}/{dotenv_filename}")
        if env_file.is_file():
            from dotenv import load_dotenv

            console.print(
                f"[yellow]Loading environment configuration from {dotenv_filename}[/]",
            )
            load_dotenv(env_file, override=True)
        return Settings()


def get_settings() -> Settings:
    return Settings.from_env()
