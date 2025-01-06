from __future__ import annotations

import binascii
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from litestar.serialization import decode_json, encode_json
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from config._base import BASE_DIR, get_env


@dataclass
class AppSettings:
    APP_LOC: str = field(default_factory=get_env("LITESTAR_APP", "app.asgi:create_app"))
    URL: str = field(default_factory=get_env("APP_URL", "http://localhost:8000"))
    DEBUG: bool = field(default_factory=get_env("LITESTAR_DEBUG", False))
    SECRET_KEY: str = field(default_factory=get_env("SECRET_KEY", binascii.hexlify(os.urandom(32)).decode(encoding="utf-8")))
    NAME: str = "Ping CRM"
    ALLOWED_CORS_ORIGINS: list[str] = field(default_factory=get_env("ALLOWED_CORS_ORIGINS", ["*"]))
    CSRF_COOKIE_NAME: str = field(default_factory=get_env("CSRF_COOKIE_NAME", "XSRF-TOKEN"))
    CSRF_HEADER_NAME: str = field(default_factory=get_env("CSRF_HEADER_NAME", "X-XSRF-TOKEN"))
    CSRF_COOKIE_SECURE: bool = field(default_factory=get_env("CSRF_COOKIE_SECURE", False))


@dataclass
class ServerSettings:
    HOST: str = field(default_factory=get_env("LITESTAR_HOST", "0.0.0.0"))  # noqa: S104
    PORT: int = field(default_factory=get_env("LITESTAR_PORT", 8000))
    KEEPALIVE: int = field(default_factory=get_env("LITESTAR_KEEPALIVE", 65))
    RELOAD: bool = field(default_factory=get_env("LITESTAR_RELOAD", False))
    RELOAD_DIRS: list[str] = field(default_factory=lambda: [f"{BASE_DIR}"])


@dataclass
class ViteSettings:
    DEV_MODE: bool = field(default_factory=get_env("VITE_DEV_MODE", False))
    USE_SERVER_LIFESPAN: bool = field(default_factory=get_env("VITE_USE_SERVER_LIFESPAN", True))
    HOST: str = field(default_factory=get_env("VITE_HOST", "0.0.0.0"))  # noqa: S104
    PORT: int = field(default_factory=get_env("VITE_PORT", 5173))
    HOT_RELOAD: bool = field(default_factory=get_env("VITE_HOT_RELOAD", True))
    ENABLE_REACT_HELPERS: bool = field(default_factory=get_env("VITE_ENABLE_REACT_HELPERS", False))
    BUNDLE_DIR: Path = Path(f"{BASE_DIR}/app/static/")
    RESOURCE_DIR: Path = Path("resources")
    TEMPLATE_DIR: Path = Path(f"{BASE_DIR}/resources/views")
    ASSET_URL: str = field(default_factory=get_env("ASSET_URL", "/static/"))


@dataclass
class DatabaseSettings:
    URL: str = field(default_factory=get_env("DATABASE_URL", "sqlite+aiosqlite:///database/pingcrm.sqlite3"))
    ECHO: bool = field(default_factory=get_env("DATABASE_ECHO", False))
    ECHO_POOL: bool = field(default_factory=get_env("DATABASE_ECHO_POOL", False))
    POOL_RECYCLE: int = field(default_factory=get_env("DATABASE_POOL_RECYCLE", 300))
    POOL_PRE_PING: bool = field(default_factory=get_env("DATABASE_PRE_POOL_PING", False))
    MIGRATION_CONFIG: str = f"{BASE_DIR}/database/migrations/alembic.ini"
    MIGRATION_PATH: str = f"{BASE_DIR}/database/migrations"
    MIGRATION_DDL_VERSION_TABLE: str = "ddl_version"
    FIXTURE_PATH: str = f"{BASE_DIR}/database/fixtures"
    _engine_instance: AsyncEngine | None = None

    @property
    def engine(self) -> AsyncEngine:
        return self.get_engine()

    def get_engine(self) -> AsyncEngine:  # pragma: no cover
        if self._engine_instance is not None:
            return self._engine_instance

        self._engine_instance = create_async_engine(
            url=self.URL,
            future=True,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            echo=self.ECHO,
            echo_pool=self.ECHO_POOL,
            pool_recycle=self.POOL_RECYCLE,
            pool_pre_ping=self.POOL_PRE_PING,
        )

        @event.listens_for(self._engine_instance.sync_engine, "connect")
        def _sqla_on_connect(
            dbapi_connection: Any,
            _: Any,
        ) -> Any:
            dbapi_connection.isolation_level = None

        @event.listens_for(self._engine_instance.sync_engine, "begin")
        def _sqla_on_begin(dbapi_connection: Any) -> Any:
            dbapi_connection.exec_driver_sql("BEGIN")

        return self._engine_instance
