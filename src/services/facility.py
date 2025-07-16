import json

from src.celery_tasks.tasks import task1
from src.connectors.redis_conn import redis
from src.exceptions.exeptions import FacilityNotFoundException
from src.schemas.facilities import AddFacility, Facility
from src.services.base import BaseService


class FacilityService(BaseService):
    async def create_facility(self, data_facility: AddFacility):
        task1.delay()
        facility = await self.db.facilities.add(data_facility)
        await self.db.commit()
        return facility

    async def get_facilities(self) -> list[Facility]:
        facilities_from_cache: str | None = await redis.get("facilities")
        if not facilities_from_cache:
            facilities = await self.db.facilities.get_all()
            facilities_json = json.dumps([f.model_dump() for f in facilities])
            await redis.set("facilities", facilities_json, 10)
            return facilities
        else:
            facilities = json.loads(facilities_from_cache)
            # facilities = [Facility.model_validate(dict_) for dict_ in json.loads(facilities_from_cache)]
        return facilities

    async def get_facilities_cached(self) -> list[Facility]:
        return await self.db.facilities.get_all()

    async def check_facilities(self, ids:list[int]):
        facilities: list[Facility] = await self.db.facilities.get_facilities_by_ids(ids)
        ids_from_db = {facility.id for facility in facilities}
        nonexistent_ids = set(ids) - ids_from_db
        if nonexistent_ids:
            raise FacilityNotFoundException(details=f"Удобства не найдены id:{list(nonexistent_ids)}")
        return facilities