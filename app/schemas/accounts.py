from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from app.schemas.base import CamelizedBaseStruct
from database.models import AccountRoles

if TYPE_CHECKING:
    from uuid import UUID


class AccountAssignment(CamelizedBaseStruct):
    team_id: UUID
    team_name: str
    is_owner: bool = False
    role: AccountRoles = AccountRoles.MEMBER


class User(CamelizedBaseStruct):
    id: UUID
    email: str
    name: str | None = None
    is_superuser: bool = False
    is_active: bool = False
    is_verified: bool = False
    has_password: bool = False
    avatar_url: str | None = None
    accounts: list[AccountAssignment] = []


class UserCreate(CamelizedBaseStruct):
    email: str
    password: str
    name: str | None = None
    is_superuser: bool = False
    is_active: bool = True
    is_verified: bool = False
    initial_account: str | None = None


class UserUpdate(CamelizedBaseStruct, omit_defaults=True):
    email: str | None | msgspec.UnsetType = msgspec.UNSET
    password: str | None | msgspec.UnsetType = msgspec.UNSET
    name: str | None | msgspec.UnsetType = msgspec.UNSET
    is_superuser: bool | None | msgspec.UnsetType = msgspec.UNSET
    is_active: bool | None | msgspec.UnsetType = msgspec.UNSET
    is_verified: bool | None | msgspec.UnsetType = msgspec.UNSET


class UserLogin(CamelizedBaseStruct):
    username: str
    password: str


class PasswordUpdate(CamelizedBaseStruct):
    current_password: str
    new_password: str


class PasswordVerify(CamelizedBaseStruct):
    current_password: str


class ProfileUpdate(CamelizedBaseStruct, omit_defaults=True):
    name: str | None | msgspec.UnsetType = msgspec.UNSET


class UserRegister(CamelizedBaseStruct):
    email: str
    password: str
    name: str | None = None
    initial_account: str | None = None
