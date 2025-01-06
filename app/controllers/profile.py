from __future__ import annotations

from typing import TYPE_CHECKING

from litestar import Controller, Request, delete, get, patch
from litestar.plugins.flash import flash
from litestar_vite.inertia import InertiaRedirect

from app import deps, schemas, services

if TYPE_CHECKING:
    from database import models as m


class ProfileController(Controller):
    include_in_schema = False
    guards = [deps.requires_active_user]

    @get(component="profile/edit", name="profile.show", path="/profile/")
    async def profile(self, current_user: m.User, users_service: services.UserService) -> schemas.User:
        """User Profile."""
        return users_service.to_schema(current_user, schema_type=schemas.User)

    @patch(component="profile/edit", name="profile.update", path="/profile/")
    async def update_profile(self, current_user: m.User, data: schemas.ProfileUpdate, users_service: services.UserService) -> schemas.User:
        """User Profile."""
        db_obj = await users_service.update(data, item_id=current_user.id)
        return users_service.to_schema(db_obj, schema_type=schemas.User)

    @patch(component="profile/edit", name="password.update", path="/profile/password-update/")
    async def update_password(self, current_user: m.User, data: schemas.PasswordUpdate, users_service: services.UserService) -> schemas.Message:
        """Update user password."""
        await users_service.update_password(data.to_dict(), db_obj=current_user)
        return schemas.Message(message="Your password was successfully modified.")

    @delete(name="account.remove", path="/profile/", status_code=303)
    async def remove_account(self, request: Request, current_user: m.User, users_service: services.UserService) -> InertiaRedirect:
        """Remove your account."""
        request.session.clear()
        _ = await users_service.delete(current_user.id)
        flash(request, "Your account has been removed from the system.", category="info")
        return InertiaRedirect(request, request.url_for("landing"))
