import json

from fastapi import APIRouter

from fastapi_cache.decorator import cache
from src.api.dependecy import DepAccess, DepDB
from src.celery_tasks.tasks import task1
from src.connectors.redis_conn import redis
from src.schemas.facilities import AddFacility

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.post("")
async def create_facility(
        # user_id: DepAccess,
        db: DepDB,
        data_facility: AddFacility
):

    task1.delay()
    facility = await db.facilities.add(data_facility)
    await db.commit()
    return {"status": "ok", "data": facility}


@router.get("")
async def get_facilities(
        db: DepDB
):
    facilities_from_cache: str | None = await redis.get("facilities")
    if not facilities_from_cache:
        print("из ДБ")
        facilities = await db.facilities.get_all()
        facilities_json = json.dumps([f.model_dump() for f in facilities])
        await redis.set("facilities", facilities_json, 10)
        return {"status": "ok", "data": facilities}
    else:
        facilities = json.loads(facilities_from_cache)
        return {"status": "ok", "data": facilities}


@router.get("/cached")
@cache(expire=60)
async def get_facilities_cached(
        db: DepDB
):
    print("получено из базы данных")
    return {"status": "ok", "data": await db.facilities.get_all()}