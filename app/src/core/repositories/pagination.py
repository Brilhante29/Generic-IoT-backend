from typing import Generic, List, TypeVar, Optional

T = TypeVar("T")


class PaginationParams:
    def __init__(self, page: int, limit: int):
        self.page = page
        self.limit = limit


class PaginatedResult(Generic[T]):
    def __init__(self, items: List[T], total: int, page: int, limit: int):
        self.items = items
        self.total = total
        self.page = page
        self.limit = limit
        self.total_pages = (total + limit - 1) // limit  # ceil division

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


def paginate(items: List[T], pagination: PaginationParams) -> PaginatedResult[T]:
    start = (pagination.page - 1) * pagination.limit
    end = start + pagination.limit
    paginated_items = items[start:end]
    return PaginatedResult(
        items=paginated_items,
        total=len(items),
        page=pagination.page,
        limit=pagination.limit,
    )
