from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as BaseSchema
from src.database import engine
from fastapi import HTTPException
from sqlalchemy import select, Insert, delete, update


class BaseRepository:
    model = None
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all(self, *args, **kwargs):
        query =  select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data: BaseSchema):
        add_hotel_stmt = Insert(self.model).values(**data.model_dump()).returning(self.model)
        print(add_hotel_stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(add_hotel_stmt)
        return result.scalars().one()

    async def edit(self, data: BaseSchema,exclude_unset = False , **filter_by):

        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        result_orm = result.scalars().all()
        if len(result_orm) > 1:
            await self.session.rollback()
            raise HTTPException(status_code=422)
        if len(result_orm) < 1:
            await self.session.rollback()
            raise HTTPException(status_code=404)

        stmt = update(self.model).filter_by(**filter_by).values(**data.model_dump(exclude_unset=exclude_unset))
        print(stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        await self.session.execute(stmt)

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