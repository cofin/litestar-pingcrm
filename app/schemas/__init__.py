from __future__ import annotations

from app.schemas import base
from app.schemas._accounts import (
    AccountLogin,
    AccountRegister,
    PasswordUpdate,
    PasswordVerify,
    ProfileUpdate,
    User,
    UserCreate,
    UserUpdate,
)


class Message(base.CamelizedBaseStruct):
    message: str


__all__ = (
    "AccountLogin",
    "AccountRegister",
    "Message",
    "PasswordUpdate",
    "PasswordVerify",
    "ProfileUpdate",
    "User",
    "UserCreate",
    "UserUpdate",
    "base",
)
