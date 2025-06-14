from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel as BaseSchema
from src.database import engine
from fastapi import HTTPException
from sqlalchemy import select, Insert, delete, update


class BaseRepository:
    model = None
    schema: BaseSchema = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, offset: int = None, limit: int = None, *args, **kwargs):
        query = select(self.model).filter_by(**kwargs)
        if offset:
            query = query.offset(offset=offset)
        if limit:
            query = query.limit(limit=limit)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [
            self.schema.model_validate(model, from_attributes=True) for model in models
        ]

    async def get_one_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if not model:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseSchema):
        add_hotel_stmt = (
            Insert(self.model).values(**data.model_dump()).returning(self.model)
        )
        print(
            add_hotel_stmt.compile(bind=engine, compile_kwargs={"literal_binds": True})
        )

        try:
            result = await self.session.execute(add_hotel_stmt)
        except IntegrityError as e:
            print("UniqueViolationError" in str(e.orig), e.orig)
            if "users_email_key" in str(e.orig):
                raise HTTPException(status_code=409)
            raise HTTPException(status_code=500)

        model = result.scalars().one_or_none()

        return self.schema.model_validate(model, from_attributes=True)

    async def edit(self, data: BaseSchema, exclude_unset=False, **filter_by):

        query = select(self.model).filter_by(**filter_by)
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
        )
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
