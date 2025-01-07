from __future__ import annotations

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from database import models as m


class OrganizationRepository(SQLAlchemyAsyncRepository[m.Organization]):
    model_type = m.Organization


class OrganizationService(SQLAlchemyAsyncRepositoryService[m.Organization]):
    repository_type = OrganizationRepository
