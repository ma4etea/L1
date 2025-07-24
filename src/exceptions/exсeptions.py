# class MyAppException(Exception):
#     details = "Неизвестная ошибка"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(self.details, *args)
#
# # -----------------------------------------------------------------------
#
# class ObjectNotFoundException(MyAppException):
#     details = "Объект не найден"
#
#
# class HotelNotFoundException(ObjectNotFoundException):
#     def __init__(self, hotel_id: int = None, details: str = "Отель не найден"):
#         self.details = details
#         if not hotel_id is None:
#             self.details = self.details + f" id: {hotel_id}"

# class MyAppException(Exception):
#     def __init__(self, details: str = "Неизвестная ошибка", *args):
#         self.details = details
#         super().__init__(self.details, *args)
#
#     def __str__(self):
#         return self.details
#
#
# class ObjectNotFoundException(MyAppException):
#     def __init__(self, details: str = "Объект не найден", *args):
#         super().__init__(details, *args)
#
#
# class HotelNotFoundException(ObjectNotFoundException):
#     def __init__(self, hotel_id: int = None, details: str = "Отель не найден", *args):
#         if hotel_id is not None:
#             details = f"{details} (id: {hotel_id})"
#         super().__init__(details, *args)
#
# class ObjectNotFoundException(ObjectNotFoundException):
#     def __init__(self, _id: int = None, details: str = "Объект не найден", *args):
#         if _id is not None:
#             details = f"{details} (id: {_id})"
#         super().__init__(details, *args)


class MyAppException(Exception):
    details = "Неизвестная ошибка"

    def __init__(self, details: str | None = None):
        if details:
            self.details = details
        super().__init__(details)

    def __str__(self):
        return self.details


class ObjectNotFoundException(MyAppException):
    object_name: str = "Объект"

    def __init__(self, object_id: int | str | list = None):
        msg = f"{self.object_name} не найден(ы)"
        if object_id is not None:
            msg += f" (id: {object_id})"
        super().__init__(msg)


class HotelNotFoundException(ObjectNotFoundException):
    object_name = "Отель"


class RoomNotFoundException(ObjectNotFoundException):
    object_name = "Номер"


class UserNotFoundException(ObjectNotFoundException):
    object_name = "Пользователь"


class BookingNotFoundException(ObjectNotFoundException):
    object_name = "Бронирование"


class BookingsNotFoundException(ObjectNotFoundException):
    object_name = "Бронирования"


class PageNotFoundException(ObjectNotFoundException):
    def __init__(self, details: str):
        self.details = details

    details = "Бронирования не найдены"


class FacilityNotFoundException(ObjectNotFoundException):
    object_name = "Удобство"


# -----------------------------------------------------------------------


class ObjectAlreadyExistsException(MyAppException):
    details = "Объект уже существует"


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    details = "Пользователь уже существует"


class HotelAlreadyExistsException(ObjectAlreadyExistsException):
    details = "Отель уже существует"


class FacilityAlreadyExistsException(ObjectAlreadyExistsException):
    details = "Удобство уже существует"


# -----------------------------------------------------------------------


class ToBigIdException(MyAppException):
    details = "Слишком большой id"


class OffsetToBigException(ToBigIdException):
    details = "Слишком большой Offset"


class LimitToBigException(ToBigIdException):
    details = "Слишком большой Limit"


class FacilityToBigIdException(ToBigIdException):
    details = "Слишком большой id для 'удобства'"


class UnexpectedResultFromDbException(MyAppException):
    details = "Неожиданный результат из db"


class StmtSyntaxErrorException(MyAppException):
    details = "Ошибка синтаксиса запроса в db"


class InvalidCredentialsException(MyAppException):
    details = "Неверные данные авторизации"


class InvalidPaginationException(MyAppException):
    details = "Неверные данные пагинации"


class NoAvailableRoom(MyAppException):
    details = "Нет доступного номера"


class InvalidDateAfterDate(MyAppException):
    details = "Дата заезда должна быть раньше выезда"


class NotNullViolationException(MyAppException):
    details = "Значение в db не может быть null"


class ObjectHaveForeignKeyException(MyAppException):
    details: str = "Объект имеет внешний ключ"

    def __init__(self, object_id: int | str | list = None):
        msg = f"{self.details}"
        if object_id is not None:
            msg += f" (id: {object_id})"
        super().__init__(msg)


class RoomHaveBookingException(ObjectHaveForeignKeyException):
    details = "Невозможно удалить номер, так как он имеет бронирование"


class HotelHaveRoomException(ObjectHaveForeignKeyException):
    details = "Невозможно удалить отель, так как у него существуют номера."


class ObjectInvalidForeignKeyException(MyAppException):
    details: str = "Объекты не связаны внешними ключами"

    def __init__(self, object_ids: list[int | str] = None, objects: list[str] = None):
        msg = f"{self.details}"
        if objects:
            msg += f" ({objects}), "
        if object_ids is not None:
            msg += f" (ids: {object_ids})"
        super().__init__(msg)


class RoomMissingToHotelException(ObjectInvalidForeignKeyException):
    details = "Номер отсутствует в отеле"
