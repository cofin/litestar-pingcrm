from __future__ import annotations

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from database import models as m


class ContactRepository(SQLAlchemyAsyncRepository[m.Contact]):
    model_type = m.Contact


class ContactService(SQLAlchemyAsyncRepositoryService[m.Contact]):
    repository_type = ContactRepository
