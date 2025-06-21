from fastapi import APIRouter

from src.api.dependecy import DepAccess, DepDB
from src.schemas.facilities import AddFacility

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.post("")
async def create_facility(
        user_id: DepAccess,
        db: DepDB,
        data_facility: AddFacility
):
    facility = await db.facilities.add(data_facility)
    await db.commit()
    return {"status": "ok", "data": facility}


@router.get("")
async def get_facilities(
        db: DepDB
):
    return {"status": "ok", "data": await db.facilities.get_all()}
