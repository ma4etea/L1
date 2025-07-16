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

class HotelAlreadyExistsException(ObjectAlreadyExistsException):
    details = "Отель уже существует"

# -----------------------------------------------------------------------


class ToBigIdException(MyAppException):
    details = "Слишком большой id"


class UnexpectedResultFromDbException(MyAppException):
    details = "Неожиданный результат из db"

class StmtSyntaxErrorException(MyAppException):
    details = "Ошибка синтаксиса запроса в db"

class InvalidCredentialsException(MyAppException):
    details = "Неверные данные авторизации"

class NoAvailableRoom(MyAppException):
    details = "Нет доступного номера"

class InvalidDateAfterDate(MyAppException):
    details = "Дата заезда должна быть раньше выезда"

class NotNullViolationException(MyAppException):
    details = "Значение в db не может быть null"