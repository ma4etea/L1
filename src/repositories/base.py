import logging
from typing import Sequence

from asyncpg import UniqueViolationError
from sqlalchemy.exc import IntegrityError, NoResultFound, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as BaseSchema
from src.database import engine, BaseModel
from sqlalchemy import select, Insert, delete, update, Executable

from src.exceptions.exeptions import ObjectNotFoundException, ToBigIdException, ObjectAlreadyExistsException
from src.exceptions.utils import is_raise
from src.repositories.mappers.base import DataMapper
from src.repositories.utils import sql_debag


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

        logging.debug(f"Запрос в базу: {sql_debag(query)}")
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

    async def get_one(self, *filter_, **filter_by):
        query = select(self.model).filter(*filter_).filter_by(**filter_by)
        model = await self.safe_execute_one(query)
        return self.mapper.to_domain(model)

    async def add(
            self,
            data: BaseSchema,
    ):
        stmt = Insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(stmt)
            model = result.scalars().one_or_none()
            return self.mapper.to_domain(model)
        except IntegrityError as exc:
            is_raise(exc, UniqueViolationError, ObjectAlreadyExistsException)
            raise exc

    async def add_bulk(self, data_list: Sequence[BaseSchema]):
        stmt = Insert(self.model).values([data.model_dump() for data in data_list])
        logging.debug(f"Запрос в базу: {sql_debag(stmt)}")

        try:
            await self.session.execute(stmt)
        except IntegrityError:
            raise ObjectNotFoundException
        except DBAPIError:
            raise ToBigIdException

    async def edit(self, data: BaseSchema, *filter_, exclude_unset=False, **filter_by):
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        ).returning(self.model)
        logging.debug(f"Запрос в базу: {sql_debag(stmt)}")
        model = await self.safe_execute_one(stmt)
        return self.mapper.to_domain(model)

    async def delete(self, **filter_by):
        await self.get_one(**filter_by)
        stmt = delete(self.model).filter_by(**filter_by)
        logging.debug(sql_debag(stmt))
        await self.session.execute(stmt)

    async def delete_bulk(self, *filter_, **filter_by):
        stmt = delete(self.model).filter(*filter_).filter_by(**filter_by)
        await self.session.execute(stmt)

    async def safe_execute_one(self, stmt: Executable) -> BaseModel:
        try:
            result = await self.session.execute(stmt)
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        except DBAPIError:
            raise ToBigIdException
        return model
