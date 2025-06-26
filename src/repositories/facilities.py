from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import Facility, AddRoomsFacilities


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesORM
    schema = AddRoomsFacilities

    async def set_facilities_to_room(self, room_id: int, facilities_ids: list[int]):
        current_facilities_ids_query = select(self.model.facility_id).filter_by(room_id=room_id)
        result = await self.session.execute(current_facilities_ids_query)
        current_facilities_ids: list[int] = list(result.scalars().all())

        existing_facilities_ids_query = select(FacilitiesOrm.id)
        result = await self.session.execute(existing_facilities_ids_query)
        existing_facilities_ids: set[int] = set(result.scalars().all())
        facilities_ids = [f for f in facilities_ids if f in existing_facilities_ids]

        delete_ids = list(set(current_facilities_ids) - set(facilities_ids))


        if delete_ids:
            delete_ids_stmt = delete(self.model).filter(self.model.facility_id.in_(delete_ids))
            await self.session.execute(delete_ids_stmt)

        if facilities_ids:
            add_ids = list(set(facilities_ids) - set(current_facilities_ids))
            if add_ids:
                add_ids_stmt = insert(self.model).values(
                    [{"room_id": room_id, "facility_id": facility_id} for facility_id in add_ids])
                await self.session.execute(add_ids_stmt)