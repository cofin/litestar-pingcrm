from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from litestar import Litestar


def create_app() -> Litestar:
    """Create ASGI application."""

    from pathlib import Path
    from uuid import UUID

    from litestar import Litestar
    from litestar.di import Provide
    from litestar.plugins.flash import FlashConfig, FlashPlugin
    from litestar.plugins.sqlalchemy import SQLAlchemyPlugin
    from litestar.stores.file import FileStore
    from litestar_granian import GranianPlugin
    from litestar_vite import VitePlugin
    from litestar_vite.inertia import InertiaPlugin

    from app import config, deps, schemas, services
    from app.cli import CommandLinePlugin
    from app.controllers.access import AccessController, RegistrationController
    from app.controllers.profile import ProfileController
    from app.controllers.site import SiteController
    from app.controllers.users import UserController
    from config import get_settings
    from database import models as m

    settings = get_settings()

    return Litestar(
        route_handlers=[AccessController, RegistrationController, ProfileController, UserController, SiteController],
        csrf_config=config.csrf,
        cors_config=config.cors,
        openapi_config=config.openapi,
        debug=settings.app.DEBUG,
        signature_namespace={"m": m, "services": services, "schemas": schemas, "UUID": UUID},
        template_config=config.templates,
        plugins=[
            GranianPlugin(),
            SQLAlchemyPlugin(config=config.alchemy),
            VitePlugin(config=config.vite),
            InertiaPlugin(config=config.inertia),
            FlashPlugin(config=FlashConfig(template_config=config.templates)),
            CommandLinePlugin(),
        ],
        stores={"session": FileStore(Path(".state/sessions"), create_directories=True)},
        middleware=[config.session.middleware],
        dependencies={
            "current_user": Provide(deps.provide_user),
            "users_service": Provide(deps.provide_users_service),
            "limit_offset": Provide(deps.provide_limit_offset_pagination, sync_to_thread=False),
            "updated_filter": Provide(deps.provide_updated_filter, sync_to_thread=False),
            "created_filter": Provide(deps.provide_created_filter, sync_to_thread=False),
            "id_filter": Provide(deps.provide_id_filter, sync_to_thread=False),
            "search_filter": Provide(deps.provide_search_filter, sync_to_thread=False),
            "order_by": Provide(deps.provide_order_by, sync_to_thread=False),
            "filters": Provide(deps.provide_filter_dependencies, sync_to_thread=False),
        },
    )
