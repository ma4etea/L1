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
