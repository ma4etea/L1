import logging
from datetime import date

from pydantic import BaseModel as BaseSchema
from sqlalchemy import select, delete, literal, union_all, insert, update
from sqlalchemy.exc import NoResultFound, DBAPIError, IntegrityError
from sqlalchemy.orm import selectinload, joinedload

from src.database import engine
from src.exceptions.exсeptions import ObjectNotFoundException, ToBigIdException
from src.models.facilities import RoomsFacilitiesORM, FacilitiesOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import RoomDataMapper, RoomWithDataMapper
from src.repositories.utils import get_available_rooms_ids, sql_debag


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_available_rooms_shymeyko(
            self,
            offset: int,
            limit: int,
            date_from: date,
            date_to: date,
            hotel_id: int,
    ):
        return await self.get_all(
            offset,
            limit,
            RoomsOrm.id.in_(get_available_rooms_ids(offset, limit, date_from, date_to, hotel_id)),
        )

    async def edit_room(self, data: BaseSchema, room_id: int, exclude_unset=False, **filter_by):
        data_dict = data.model_dump(exclude_unset=exclude_unset, exclude={"facilities_ids"})

        if data_dict:
            stmt = (update(self.model).filter_by(id=room_id, **filter_by).values(**data_dict)).returning(
                self.model
            )
        else:
            stmt = select(self.model).filter_by(id=room_id, **filter_by)

        if data.facilities_ids is not None:
            fac_ids = data.facilities_ids
            rf = RoomsFacilitiesORM
            f = FacilitiesOrm
            """ ----------------------------------------------------------------------------------------
            Получает список id rooms_facilities,
                это facilities которые отсутствуют в запросе, но есть у room, их нужно удалить.
    
            with delete_rooms_facilities_ids as (
                select rf.id as rooms_facilities_id from rooms_facilities rf
                where rf.room_id = 17 and rf.facility_id not in (8,9,11)
            ),
            """
            delete_rooms_facilities_ids = (
                select(rf.id.label("rooms_facilities_id"))
                .select_from(rf)
                .filter(rf.room_id == room_id, rf.facility_id.notin_(fac_ids))
                .cte("delete_rooms_facilities_ids")
            )

            """ ----------------------------------------------------------------------------------------
            Удаляет связь rooms_facilities по списку id, которые получает из delete_rooms_facilities_ids    
    
            deleted as (
                delete from rooms_facilities where rooms_facilities.id in (select rooms_facilities_id from delete_rooms_facilities_ids)
                )
            """
            deleted = (
                delete(rf)
                .filter(
                    rf.id.in_(
                        select(delete_rooms_facilities_ids.c.rooms_facilities_id).select_from(
                            delete_rooms_facilities_ids
                        )
                    )
                )
                .cte("deleted")
            )

            if deleted is not None:
                stmt = stmt.add_cte(
                    deleted
                )  # new_case .add_cte(deleted) присоединяет к запросу deleted

            if fac_ids:
                """ ----------------------------------------------------------------------------------------
                Получает список id facilities, 
                    это facilities которые есть в запросе но нет у room, их нужно добавить, 
                    дополнительно проверяет что facilities.id существует в базе          
                    
                add_facilities_ids as (
                    select id as facilities_id from (values (8),(9),(11)) as vals(id)
                    where id not in (select rf.facility_id from rooms_facilities rf where rf.room_id = 17) and id in (select f.id from facilities f)
                    ),
                """
                vals = [select(literal(i).label("id")) for i in fac_ids]
                vals_union = union_all(*vals).alias("vals")
                add_facilities_ids = (
                    select(vals_union.c.id.label("facilities_id"))
                    .select_from(vals_union)
                    .filter(
                        vals_union.c.id.notin_(
                            select(rf.facility_id).select_from(rf).filter(rf.room_id == room_id)
                        ),
                        vals_union.c.id.in_(select(f.id).select_from(f)),
                    )
                    .cte("add_facilities_ids")
                )

                """ ----------------------------------------------------------------------------------------         
                Добавляет связи rooms_facilities, из списка add_facilities_ids
                
                insert into rooms_facilities (room_id, facility_id)
                    select 17, facilities_id from add_facilities_ids"""

                # new_case insert+select можно так [col.name for col in rf.columns] или конкретно ["room_id", "facility_id"]
                # new_case это literal(room_id) подставляем конкретное значение
                add_facilities = (
                    insert(rf)
                    .from_select(
                        ["room_id", "facility_id"],
                        select(
                            literal(room_id),
                            add_facilities_ids.c.facilities_id,
                        ),
                    )
                    .cte("add_facilities")
                )
                if add_facilities is not None:
                    stmt = stmt.add_cte(add_facilities)

        logging.debug(sql_debag(stmt))

        """IntegrityError, DBAPIError"""
        try:
            result = await self.session.execute(stmt)
            room_orm = result.scalar_one()
            return self.mapper.to_domain(room_orm)
        except  NoResultFound:
            raise ObjectNotFoundException
        except DBAPIError:
            raise ToBigIdException


    async def get_rooms_with(self, **filter_by):
        query = (
            select(self.model).filter_by(**filter_by).options(selectinload(self.model.facilities))
        )
        logging.debug(sql_debag(query))
        try:
            res = await self.session.execute(query)
            models = res.scalars().all()
        except DBAPIError:
            raise ToBigIdException
        return [RoomWithDataMapper.to_domain(model) for model in models]

    async def get_room_with(self, **filter_by):
        query = select(self.model).options(joinedload(self.model.facilities)).filter_by(**filter_by)
        try:
            res = await self.session.execute(query)
            model = res.unique().scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        except DBAPIError:
            raise ToBigIdException
        return RoomWithDataMapper.to_domain(model)
