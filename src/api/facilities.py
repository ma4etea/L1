from fastapi import APIRouter, Body, Path

from fastapi_cache.decorator import cache
from src.api.dependecy import DepAccess, DepDB
from src.api.http_exceptions.http_exeptions import FacilityAlreadyExistsHTTPException, FacilityNotFoundHTTPException
from src.exceptions.exeptions import FacilityAlreadyExistsException
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
    try:
        facility = await FacilityService(db).create_facility(data_facility)
    except FacilityAlreadyExistsException:
        raise FacilityAlreadyExistsHTTPException
    return {"status": "ok", "data": facility}


# @router.get("")
async def get_facilities(db: DepDB):
    facilities = await FacilityService(db).get_facilities()
    return {"status": "ok", "data": facilities}


@router.get("")
@cache(expire=60)
async def get_facilities(db: DepDB):
    facilities = await FacilityService(db).get_facilities_cached()
    return {"status": "ok", "data": facilities}


@router.put("/{facility_id}")
async def update_facility(
        _: DepAccess,
        db: DepDB,
        data_facility: AddFacility = Body(openapi_examples=openapi_facility_examples),
        facility_id: int = Path(ge=1)):
    try:
        facility = await FacilityService(db).update_facility(data_facility, facility_id)
    except :
        raise FacilityNotFoundHTTPException

    return {"status": "ok", "data": facility}

