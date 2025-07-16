from fastapi import HTTPException


class MyAppHTTPException(HTTPException):
    status_code = 500
    details = "Ошибка сервера"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.details)


#------------------------------------------------------------------------------

class HotelNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Отель не найден"


class RoomNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Номер не найден"

class RoomsNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Номера не найдены"

class UserNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Пользователь не найден"


class BookingNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Бронирование не найдено"


class FacilityNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Удобство не найдено"

#------------------------------------------------------------------------------
class UserAlreadyExistsHTTPException(MyAppHTTPException):
    status_code = 409
    details = "Пользователь уже существует"

class HotelAlreadyExistsHTTPException(MyAppHTTPException):
    status_code = 409
    details = "Отель уже существует"
#------------------------------------------------------------------------------

class ToBigIdHTTPException(MyAppHTTPException):
    status_code = 400
    details = "ИД слишком большой"

class InvalidCredentialsHTTPException(MyAppHTTPException):
    status_code = 401
    details = "Неверные логин и/или пароль"

class NoAvailableRoomHTTPException(MyAppHTTPException):
    status_code = 409
    details = "Нет доступного номера для бронирования"

class InvalidDateAfterDateHTTPException(MyAppHTTPException):
    status_code = 422
    details = "Дата заезда должна быть раньше выезда"

class InvalidTokenHTTPException(MyAppHTTPException):
    status_code = 401
    details = "Токен отсутствует"

class IncorrectTokenHTTPException(MyAppHTTPException):
    status_code = 401
    details = "Неверный токен"

class ExpiredTokenHTTPException(MyAppHTTPException):
    status_code = 401
    details = "Токен истек"

class StmtSyntaxErrorHTTPException(MyAppHTTPException):
    status_code = 400
    details = "Ошибка запроса"

class NotNullViolationHTTPException(MyAppHTTPException):
    status_code = 400
    details = "Значение не может быть null"

