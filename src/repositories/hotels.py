
from sqlalchemy import func, select

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







