from fastapi import APIRouter

from fastapi_cache.decorator import cache
from src.api.dependecy import DepAccess, DepDB
from src.schemas.facilities import AddFacility
from src.services.facility import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])

@router.post("")
async def create_facility(_: DepAccess, db: DepDB, data_facility: AddFacility):
    facility = await FacilityService(db).create_facility(data_facility)
    return {"status": "ok", "data": facility}


@router.get("")
async def get_facilities(db: DepDB):
    facilities = await FacilityService(db).get_facilities()
    return {"status": "ok", "data": facilities}


@router.get("/cached")
@cache(expire=60)
async def get_facilities_cached(db: DepDB):
    facilities = await FacilityService(db).get_facilities_cached()
    return {"status": "ok", "data": facilities}
