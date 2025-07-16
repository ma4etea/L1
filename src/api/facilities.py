from fastapi import APIRouter, Body

from fastapi_cache.decorator import cache
from src.api.dependecy import DepAccess, DepDB
from src.schemas.facilities import AddFacility
from src.services.facility import FacilityService

openapi_facility_examples = {
    "1": {
        "summary": "Табурет",
        "value": {
            "title": "Табурет"
        },
    },
    "2": {
        "summary": "Кондиционер",
        "value": {
            "title": "Кондиционер"
        },
    },
    "3": {
        "summary": "Телевизор",
        "value": {
            "title": "Телевизор"
        },
    },
    "4": {
        "summary": "Джакузи",
        "value": {
            "title": "Джакузи"
        },
    },
    "5": {
        "summary": "Балкон",
        "value": {
            "title": "Балкон"
        },
    },
}


router = APIRouter(prefix="/facilities", tags=["Удобства"])

@router.post("")
async def create_facility(
        _: DepAccess, db: DepDB,
        data_facility: AddFacility = Body(openapi_examples=openapi_facility_examples)):
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
