from typing import Annotated

from fastapi import Query, Depends
from pydantic import BaseModel


class Pagination(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="какая страницы")]
    per_page: Annotated[int | None,  Query(3, ge=1, le=50, description="Сколько в странице")]

PaginationDep = Annotated[Pagination, Depends()]