from __future__ import annotations

from app.schemas import base
from app.schemas.accounts import AccountAssignment, PasswordUpdate, PasswordVerify, ProfileUpdate, User, UserCreate, UserLogin, UserRegister, UserUpdate


class Message(base.CamelizedBaseStruct):
    message: str


__all__ = (
    "AccountAssignment",
    "Message",
    "PasswordUpdate",
    "PasswordVerify",
    "ProfileUpdate",
    "User",
    "UserCreate",
    "UserLogin",
    "UserRegister",
    "UserUpdate",
    "base",
)
