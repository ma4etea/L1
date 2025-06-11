from fastapi import HTTPException
from sqlalchemy import func, select, Insert, delete, update
from pydantic import BaseModel as BaseSchema
from src.database import engine
from src.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsOrm

    async def get_all(self, title, location, offset, limit):
        query = select(self.model)

        if title:
            query = query.where(HotelsOrm.title.ilike(f'%{title.strip()}%'))

        if location:
            query = query.where(func.lower(HotelsOrm.location).contains(location.strip().lower()))

        print(query.compile(compile_kwargs={"literal_binds": True}))

        query = (
            query
            .limit(limit=limit)
            .offset(offset=offset)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def add(self, data: BaseSchema):
        add_hotel_stmt = Insert(self.model).values(**data.model_dump()).returning(self.model)
        print(add_hotel_stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(add_hotel_stmt)
        return result.scalars().one()

    async def edit(self, data: BaseSchema, **filter_by):

        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        result_orm = result.scalars().all()
        if len(result_orm) > 1:
            await self.session.rollback()
            raise HTTPException(status_code=422)
        if len(result_orm) < 1:
            await self.session.rollback()
            raise HTTPException(status_code=404)

        stmt = update(self.model).filter_by(**filter_by).values(**data.model_dump())
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





