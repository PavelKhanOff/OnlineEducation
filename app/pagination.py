from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractPage, AbstractParams

T = TypeVar("T")


class CustomPage(AbstractPage[T], Generic[T]):
    data: Sequence[T]
    meta: dict
    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ):
        return cls(
            data=items,
            meta={
                "current_page": params.page,
                "per_page": params.size,
                "total_items": total,
            },
        )
