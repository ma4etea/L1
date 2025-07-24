from sqlalchemy import select, delete, insert

from src.models.facilities import FacilitiesOrm, RoomsFacilitiesORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import AddRoomsFacilities


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper

    async def get_facilities_by_ids(self, ids: list[int]):
        if not ids:
            return []
        return await self.get_all(None, None, self.model.id.in_(ids))


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
                    [{"room_id": room_id, "facility_id": facility_id} for facility_id in add_ids]
                )
                await self.session.execute(add_ids_stmt)

    async def get_facilities_with_by_rooms_ids(self, room_ids) -> list[dict]:
        """
        SELECT rf.room_id, f.*
        FROM rooms_facilities rf
        JOIN facilities f ON rf.facility_id = f.id
        WHERE rf.room_id IN (1, 2, 3, 4);
        """
        rf = self.model
        f = FacilitiesOrm
        query = (
            select(rf.room_id, f.id, f.title)
            .select_from(rf)
            .join(f, rf.facility_id == f.id)
            .filter(rf.room_id.in_(room_ids))
            .order_by(rf.room_id)
        )
        res = await self.session.execute(query)
        rows = res.mappings().all()
        return [dict(row) for row in rows]
