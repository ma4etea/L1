from datetime import date

from fastapi import HTTPException


class MyAppExceptions(Exception):
    details = "Неизвестная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.details, *args)


class ObjectNotFound(MyAppExceptions):
    details = "Объект не найден"


class ToBigId(MyAppExceptions):
    details = "Слишком большой id"


class UnexpectedResultFromDb(MyAppExceptions):
    details = "Неожиданный результат из db"


class ObjectAlreadyExists(MyAppExceptions):
    details = "Объект уже существует"


def check_data_from_after_date_to(date_from: date, date_to: date):
    if date_from <= date_to:
        raise HTTPException(422, "date_from должно быть больше date_to")


class MyAppHTTPException(HTTPException):
    status_code = 500
    details = "Ошибка сервера"
    def __init__(self):

        super().__init__(status_code = self.status_code, detail=self.details)

class HotelNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Отель не найден"

class RoomNotFoundHTTPException(MyAppHTTPException):
    status_code = 404
    details = "Номер не найден"

class ToBigIdHTTPException(MyAppHTTPException):
    status_code = 400
    details = "ИД слишком большой"
