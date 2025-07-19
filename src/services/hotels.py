import logging
from datetime import date

from PIL.ImageChops import offset

from src.api.dependecy import DepPagination
from src.exceptions.exсeptions import ObjectNotFoundException, HotelNotFoundException, HotelAlreadyExistsException, \
    ObjectAlreadyExistsException
from src.exceptions.utils import check_data_from_after_date_to_http_exc
from src.schemas.hotels import HotelAdd, HotelPatch, Hotel
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_available_hotels(
            self,
            date_from: date,
            date_to: date,
            page: int,
            per_page: int,
            title: str | None = None,
            location: str | None = None,

    ):
        offset, limit = self.get_pagination_with_check(page, per_page)
        hotels = await self.db.hotels.get_available_hotels(
            title, location, offset, limit, date_from=date_from, date_to=date_to
        )
        if not hotels:
            raise HotelNotFoundException
        return hotels

    async def add_hotel(self, hotel_data: HotelAdd ):
        try:
            hotel = await self.db.hotels.add(hotel_data)
        except ObjectAlreadyExistsException:
            raise HotelAlreadyExistsException
        await self.db.commit()
        return hotel

    async def get_hotel(self, hotel_id: int):
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException as exc:
            raise HotelNotFoundException from exc

    async def delete_hotel(self, hotel_id: int):
        await self.check_hotel(hotel_id)
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def check_hotel(self, hotel_id):
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException as exc:
            logging.warning(f"Отель не найден: {type(exc).__name__}")
            raise HotelNotFoundException(hotel_id) from exc


    async def edit_hotel(self, hotel_id: int, hotel_data: HotelPatch | HotelAdd, exclude_unset=False) -> Hotel:
        try:
            hotel = await self.db.hotels.edit(hotel_data, exclude_unset=exclude_unset, id=hotel_id)
        except ObjectNotFoundException as exc:
            raise HotelNotFoundException from exc
        await self.db.commit()
        return hotel