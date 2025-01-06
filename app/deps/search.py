"""Application dependency providers."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from advanced_alchemy.filters import (
    BeforeAfter,
    CollectionFilter,
    FilterTypes,
    LimitOffset,
    OrderBy,
    SearchFilter,
)
from litestar.params import Dependency, Parameter

DTorNone = datetime | None
StringOrNone = str | None
UuidOrNone = UUID | None
BooleanOrNone = bool | None
SortOrderOrNone = Literal["asc", "desc"] | None


def provide_id_filter(ids: list[int] | None = Parameter(query="ids", default=None, required=False)) -> CollectionFilter[int]:
    return CollectionFilter(field_name="id", values=ids or [])


def provide_created_filter(
    before: DTorNone = Parameter(query="createdBefore", default=None, required=False),
    after: DTorNone = Parameter(query="createdAfter", default=None, required=False),
) -> BeforeAfter:
    return BeforeAfter("created_at", before, after)


def provide_search_filter(
    field: StringOrNone = Parameter(title="Field to search", query="searchField", default=None, required=False),
    search: StringOrNone = Parameter(title="Field to search", query="searchString", default=None, required=False),
    ignore_case: BooleanOrNone = Parameter(title="Search should be case sensitive", query="searchIgnoreCase", default=None, required=False),
) -> SearchFilter:
    return SearchFilter(field_name=field, value=search, ignore_case=ignore_case or False)  # type: ignore[arg-type]


def provide_order_by(
    field_name: StringOrNone = Parameter(title="Order by field", query="orderBy", default="updated_at", required=False),
    sort_order: SortOrderOrNone = Parameter(title="Field to search", query="sortOrder", default="desc", required=False),
) -> OrderBy:
    return OrderBy(field_name=field_name, sort_order=sort_order)  # type: ignore[arg-type]


def provide_updated_filter(
    before: DTorNone = Parameter(query="updatedBefore", default=None, required=False),
    after: DTorNone = Parameter(query="updatedAfter", default=None, required=False),
) -> BeforeAfter:
    return BeforeAfter("updated_at", before, after)


def provide_limit_offset_pagination(
    current_page: int = Parameter(ge=1, query="currentPage", default=1, required=False),
    page_size: int = Parameter(query="pageSize", ge=1, default=10, required=False),
) -> LimitOffset:
    return LimitOffset(page_size, page_size * (current_page - 1))


def provide_filter_dependencies(
    created_filter: BeforeAfter = Dependency(skip_validation=True),
    updated_filter: BeforeAfter = Dependency(skip_validation=True),
    id_filter: CollectionFilter = Dependency(skip_validation=True),
    limit_offset: LimitOffset = Dependency(skip_validation=True),
    search_filter: SearchFilter = Dependency(skip_validation=True),
    order_by: OrderBy = Dependency(skip_validation=True),
) -> list[FilterTypes]:
    filters: list[FilterTypes] = []
    if id_filter.values:
        filters.append(id_filter)
    filters.extend([created_filter, limit_offset, updated_filter])

    if search_filter.field_name is not None and search_filter.value is not None:
        filters.append(search_filter)
    if order_by.field_name is not None:
        filters.append(order_by)
    return filters
