from __future__ import annotations

import asyncio
import base64

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

hasher = PasswordHash((Argon2Hasher(),))


def get_encryption_key(secret: str) -> bytes:
    """Get Encryption Key."""
    if len(secret) <= 32:
        secret = f"{secret:<32}"[:32]
    return base64.urlsafe_b64encode(secret.encode())


async def get_password_hash(password: str | bytes) -> str:
    """Get password hash."""
    return await asyncio.get_running_loop().run_in_executor(None, hasher.hash, password)


async def verify_password(plain_password: str | bytes, hashed_password: str) -> bool:
    """Verify Password."""
    valid, _ = await asyncio.get_running_loop().run_in_executor(
        None,
        hasher.verify_and_update,
        plain_password,
        hashed_password,
    )
    return bool(valid)
