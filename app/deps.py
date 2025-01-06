"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar.exceptions import PermissionDeniedException
from litestar.middleware.session.server_side import ServerSideSessionBackend
from litestar.security.session_auth import SessionAuth
from litestar_vite.inertia import share

from app import config, schemas, services
from database import models as m

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar.connection import ASGIConnection, Request
    from litestar.handlers.base import BaseRouteHandler
    from sqlalchemy.ext.asyncio import AsyncSession


async def provide_user(request: Request[m.User, Any, Any]) -> m.User:
    """Get the user from the connection."""
    return request.user


async def provide_users_service(db_session: AsyncSession) -> AsyncGenerator[services.UserService, None]:
    """Construct repository and service objects for the request."""
    async with services.UserService.new(
        session=db_session,
        error_messages={
            "duplicate_key": "A user with this email already exists",
            "foreign_key": "A user with this email already exists",
            "integrity": "User operation failed.",
        },
    ) as service:
        yield service


def requires_active_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Request requires active user."""
    if connection.user.is_active:
        return
    msg = "Your user account is inactive."
    raise PermissionDeniedException(detail=msg)


def requires_superuser(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Request requires active superuser."""
    if connection.user.is_superuser:
        return
    msg = "Your account does not have enough privileges to access this content."
    raise PermissionDeniedException(detail=msg)


def requires_verified_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Verify the connection user is a superuser."""
    if connection.user.is_verified:
        return
    msg = "Your account has not been verified."
    raise PermissionDeniedException(detail=msg)


async def current_user_from_session(
    session: dict[str, Any],
    connection: ASGIConnection[Any, Any, Any, Any],
) -> m.User | None:
    """Lookup current user from server session state."""

    if (user_id := session.get("user_id")) is None:
        share(connection, "auth", {"isAuthenticated": False})
        return None
    service = await anext(provide_users_service(config.alchemy.provide_session(connection.app.state, connection.scope)))
    user = await service.get_one_or_none(email=user_id)
    if user and user.is_active:
        share(connection, "auth", {"isAuthenticated": True, "user": service.to_schema(user, schema_type=schemas.User)})
        return user
    share(connection, "auth", {"isAuthenticated": False})
    return None


session_auth = SessionAuth[m.User, ServerSideSessionBackend](
    session_backend_config=config.session,
    retrieve_user_handler=current_user_from_session,
    exclude=[
        "^/schema",
        "^/health",
        "^/login",
        "^/register",
        "^/o/",
    ],
)
