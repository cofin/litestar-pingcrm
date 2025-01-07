from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID  # noqa: TC003

from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(UUIDv7AuditBase):
    __tablename__ = "user_account"

    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(nullable=True, default=None)
    hashed_password: Mapped[str | None] = mapped_column(String(length=255), nullable=True, default=None)
    avatar_url: Mapped[str | None] = mapped_column(String(length=500), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verified_at: Mapped[date] = mapped_column(nullable=True, default=None)
    joined_at: Mapped[date] = mapped_column(default=datetime.now)
    accounts: Mapped[list[AccountMember]] = relationship(back_populates="user", uselist=True, cascade="all, delete")

    @hybrid_property
    def has_password(self) -> bool:
        return self.hashed_password is not None


class AccountRoles(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class AccountMember(UUIDv7AuditBase):
    __tablename__ = "account_member"
    __table_args__ = (UniqueConstraint("user_id", "account_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id", ondelete="cascade"), nullable=False)
    user: Mapped[User] = relationship(back_populates="accounts", foreign_keys="AccountMember.user_id", innerjoin=True, uselist=False)
    name: AssociationProxy[str] = association_proxy("user", "name")
    email: AssociationProxy[str] = association_proxy("user", "email")

    account_id: Mapped[UUID] = mapped_column(ForeignKey("account.id", ondelete="cascade"), nullable=False)
    account: Mapped[Account] = relationship(back_populates="members", foreign_keys="AccountMember.account_id", innerjoin=True, uselist=False, lazy="joined")
    account_name: AssociationProxy[str] = association_proxy("account", "name")
    role: Mapped[AccountRoles] = mapped_column(String(length=50), default=AccountRoles.MEMBER, nullable=False, index=True)
    is_owner: Mapped[bool] = mapped_column(default=False, nullable=False)


class Account(UUIDv7AuditBase):
    __tablename__ = "account"

    name: Mapped[str]
    members: Mapped[list[AccountMember]] = relationship(back_populates="account", cascade="all, delete", lazy="noload", passive_deletes=True)
    organizations: Mapped[list[Organization]] = relationship(back_populates="account", cascade="all, delete")
    contacts: Mapped[list[Contact]] = relationship(back_populates="account", cascade="all, delete")


class Organization(UUIDv7AuditBase):
    __tablename__ = "organization"

    name: Mapped[str]
    email: Mapped[str | None]
    phone: Mapped[str | None]
    address: Mapped[str | None]
    city: Mapped[str | None]
    region: Mapped[str | None]
    country: Mapped[str | None]
    postal_code: Mapped[str | None]

    account_id: Mapped[UUID] = mapped_column(ForeignKey("account.id", ondelete="cascade"), nullable=False)
    account: Mapped[Account] = relationship(back_populates="organizations", foreign_keys="Organization.account_id", viewonly=True, innerjoin=True)

    contacts: Mapped[list[Contact]] = relationship(back_populates="organization", cascade="all, delete")


class Contact(UUIDv7AuditBase):
    __tablename__ = "contact"

    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str | None]
    phone: Mapped[str | None]
    address: Mapped[str | None]
    city: Mapped[str | None]
    region: Mapped[str | None]
    country: Mapped[str | None]
    postal_code: Mapped[str | None]

    account_id: Mapped[UUID] = mapped_column(ForeignKey("account.id", ondelete="cascade"), nullable=False)
    account: Mapped[Account] = relationship(back_populates="contacts", foreign_keys="Contact.account_id", viewonly=True, innerjoin=True)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey(Organization.id), nullable=False)
    organization: Mapped[Organization] = relationship(back_populates="contacts", viewonly=True, innerjoin=True)

    @hybrid_property
    def name(self) -> str:
        return f"{self.last_name} {self.first_name}"
