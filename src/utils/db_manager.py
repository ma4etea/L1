from sqlalchemy.ext.asyncio import async_sessionmaker
from src.repositories.auth import AuthRepository
from src.repositories.booking import BookingsRepository
from src.repositories.facilities import FacilitiesRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository



# new_case асинхронный контекстный менеджер для обращения к базе данных
class DBManager:
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    async def __aenter__(self):

        self.session = self.session_factory()

        self.auth = AuthRepository(self.session)
        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()



































# class DBManager:
#
#     def __init__(self, session_factory: AsyncSession):
#         self.session_factory = session_factory
#
#     async def __aenter__(self):
#         self.session = self.session_factory
#
#         self.auth = AuthRepository(self.session)
#         self.hotels = HotelsRepository(self.session)
#         self.rooms = RoomsRepository(self.session)
#         return self
#
#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         await self.session.rollback()
#         await self.session.close()
#
#     async def commit(self):
#         await self.session.commit()
#
#     async def rollback(self):
#         await self.session.rollback()
