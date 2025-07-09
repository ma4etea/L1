class MyAppException(Exception):
    details = "Неизвестная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.details, *args)

# -----------------------------------------------------------------------

class ObjectNotFoundException(MyAppException):
    details = "Объект не найден"


class HotelNotFoundException(ObjectNotFoundException):
    details = "Отель не найден"


class RoomNotFoundException(ObjectNotFoundException):
    details = "Номер не найден"


class UserNotFoundException(ObjectNotFoundException):
    details = "Пользователь не найден"


class BookingNotFoundException(ObjectNotFoundException):
    details = "Бронирование не найдено"


class FacilityNotFoundException(ObjectNotFoundException):
    details = "Удобство не найдено"


# -----------------------------------------------------------------------

class ObjectAlreadyExistsException(MyAppException):
    details = "Объект уже существует"


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    details = "Пользователь уже существует"

# -----------------------------------------------------------------------


class ToBigIdException(MyAppException):
    details = "Слишком большой id"


class UnexpectedResultFromDbException(MyAppException):
    details = "Неожиданный результат из db"

class InvalidCredentialsException(MyAppException):
    details = "Неверные данные авторизации"

class NoAvailableRoom(MyAppException):
    details = "Нет доступного номера"