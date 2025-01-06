from __future__ import annotations

from typing import TYPE_CHECKING, Any

from litestar import Controller, Request, get, post
from litestar.plugins.flash import flash
from litestar_vite.inertia import InertiaRedirect

if TYPE_CHECKING:
    from app import schemas, services


class AccessController(Controller):
    include_in_schema = False
    exclude_from_auth = True
    cache = False

    @get(component="Auth/Login", name="login", path="/login/")
    async def show_login(self, request: Request) -> InertiaRedirect | dict[str, Any]:
        """Show the user login page."""
        if request.session.get("user_id", False):
            flash(request, "Your account is already authenticated.", category="info")
            return InertiaRedirect(request, request.url_for("dashboard"))
        return {}

    @post(component="Auth/Login", name="login.check", path="/login/")
    async def login(self, request: Request[Any, Any, Any], users_service: services.UserService, data: schemas.AccountLogin) -> InertiaRedirect:
        """Authenticate a user."""
        user = await users_service.authenticate(data.username, data.password)
        request.set_session({"user_id": user.email})
        flash(request, "Your account was successfully authenticated.", category="info")
        return InertiaRedirect(request, request.url_for("dashboard"))

    @post(name="logout", path="/logout/", exclude_from_auth=False)
    async def logout(self, request: Request) -> InertiaRedirect:
        """Account Logout"""
        flash(request, "You have been logged out.", category="info")
        request.clear_session()
        return InertiaRedirect(request, request.url_for("login"))


class RegistrationController(Controller):
    include_in_schema = False
    exclude_from_auth = True
    cache = False

    @get(component="auth/register", name="register", path="/register/")
    async def show_signup(self, request: Request) -> InertiaRedirect | dict[str, str]:
        """Show the user login page."""
        if request.session.get("user_id", False):
            flash(request, "Your account is already authenticated.  Welcome back!", category="info")
            return InertiaRedirect(request, request.url_for("dashboard"))
        return {}

    @post(component="auth/register", name="register.add", path="/register/")
    async def signup(self, request: Request, users_service: services.UserService, data: schemas.AccountRegister) -> InertiaRedirect:
        """User Signup."""
        user = await users_service.create(data.to_dict())
        request.set_session({"user_id": user.email})
        request.app.emit(event_id="user_created", user_id=user.id)
        flash(request, "Account created successfully.  Welcome!", category="info")
        return InertiaRedirect(request, request.url_for("dashboard"))
