"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from litestar import Controller, delete, get, patch, post
from litestar.params import Dependency, Parameter

from app import deps, schemas, services

if TYPE_CHECKING:
    from advanced_alchemy.filters import FilterTypes
    from advanced_alchemy.service import OffsetPagination


class UserController(Controller):
    """User Account Controller."""

    tags = ["User Accounts"]
    guards = [deps.requires_superuser]

    @get(operation_id="ListUsers", name="users:list", path="/api/users", cache=60)
    async def list_users(self, users_service: services.UserService, filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)]) -> OffsetPagination[schemas.User]:
        """List users."""
        results, total = await users_service.list_and_count(*filters)
        return users_service.to_schema(data=results, total=total, schema_type=schemas.User, filters=filters)

    @get(operation_id="GetUser", name="users:get", path="/api/users/{email:str}")
    async def get_user(self, users_service: services.UserService, email: Annotated[str, Parameter(title="User Email", description="The user to retrieve.")]) -> schemas.User:
        """Get a user."""
        db_obj = await users_service.get_one(email=email)
        return users_service.to_schema(db_obj, schema_type=schemas.User)

    @post(operation_id="CreateUser", name="users:create", cache_control=None, path="/api/users")
    async def create_user(self, users_service: services.UserService, data: schemas.UserCreate) -> schemas.User:
        """Create a new user."""
        db_obj = await users_service.create(data.to_dict())
        return users_service.to_schema(db_obj, schema_type=schemas.User)

    @patch(operation_id="UpdateUser", name="users:update", path="/api/users/{email:str}")
    async def update_user(
        self,
        data: schemas.UserUpdate,
        users_service: services.UserService,
        email: Annotated[str, Parameter(title="User Email", description="The user to update.")],
    ) -> schemas.User:
        """Create a new user."""
        db_obj = await users_service.update(item_id=email, data=data, id_attribute="email")
        return users_service.to_schema(db_obj, schema_type=schemas.User)

    @delete(operation_id="DeleteUser", name="users:delete", path="/api/users/{email:str}")
    async def delete_user(self, users_service: services.UserService, email: Annotated[str, Parameter(title="User Email", description="The user to delete.")]) -> None:
        """Delete a user from the system."""
        _ = await users_service.delete_where(email=email)
