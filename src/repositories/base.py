from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as BaseSchema
from src.database import engine, BaseModel
from fastapi import HTTPException
from sqlalchemy import select, Insert, delete, update

from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model: BaseModel = None
    mapper: DataMapper = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, offset: int = None, limit: int = None, *args, **kwargs):
        query = select(self.model).filter(*args).filter_by(**kwargs)
        if offset:
            query = query.offset(offset=offset)
        if limit:
            query = query.limit(limit=limit)

        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self.mapper.to_domain(model) for model in models]

    async def get_one_none(self, *filter_, **filter_by):
        query = select(self.model).filter(*filter_).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if not model:
            return None
        return self.mapper.to_domain(model)

    async def add(
        self,
        data: BaseSchema,
    ):
        stmt = Insert(self.model).values(**data.model_dump()).returning(self.model)
        print(stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))

        try:
            result = await self.session.execute(stmt)
        except IntegrityError as e:
            print("UniqueViolationError" in str(e.orig), e.orig)
            if "users_email_key" in str(e.orig):
                raise HTTPException(status_code=409)
            raise HTTPException(status_code=500)

        model = result.scalars().one_or_none()

        return self.mapper.to_domain(model)

    async def add_bulk(self, data_list: list[BaseSchema]):
        stmt = Insert(self.model).values([data.model_dump() for data in data_list])
        print(stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        await self.session.execute(stmt)

    async def edit(self, data: BaseSchema, *filter_, exclude_unset=False, **filter_by):
        query = select(self.model).filter(*filter_).filter_by(**filter_by)
        result = await self.session.execute(query)
        result_orm = result.scalars().all()
        if len(result_orm) > 1:
            raise HTTPException(status_code=422)
        if len(result_orm) < 1:
            raise HTTPException(status_code=404)

        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        ).returning(self.model)
        print("----------------------....................................")
        print(stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()
        if not model:
            raise HTTPException(404)
        return self.mapper.to_domain(model)

    async def delete(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        result_orm = result.scalars().all()
        if len(result_orm) > 1:
            await self.session.rollback()
            raise HTTPException(status_code=422)
        if len(result_orm) < 1:
            await self.session.rollback()
            raise HTTPException(status_code=404)

        stmt = delete(self.model).filter_by(**filter_by)
        print(stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        await self.session.execute(stmt)

    async def delete_bulk(self, *filter_, **filter_by):
        stmt = delete(self.model).filter(*filter_).filter_by(**filter_by)
        await self.session.execute(stmt)
