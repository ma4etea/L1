
from sqlalchemy import func, select

from src.models.hotels import HotelsOrm
from src.repositories.base import BaseRepository
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

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
        models = result.scalars().all()
        return [self.schema.model_validate(model, from_attributes=True) for model in models]







