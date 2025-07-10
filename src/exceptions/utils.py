from datetime import date
from typing import Type, Tuple, TypeVar

from fastapi import HTTPException


def check_data_from_after_date_to_http_exc(date_from: date, date_to: date):
    if date_from <= date_to:
        raise HTTPException(422, "date_from должно быть больше date_to")


T = TypeVar("T", bound=BaseException)


def is_raise(
        exc: Exception,
        reason: Type[BaseException] | Tuple[Type[BaseException], ...],
        to_raise: Type[T]
) -> None:
    """
    Проверяет, было ли исходное исключение (`exc`) вызвано ошибкой заданного типа (`reason`)
    внутри цепочки исключений (`__cause__`) и, если да — выбрасывает новое исключение (`to_raise`).

    Полезно при анализе вложенных ошибок, например, при обработке IntegrityError от SQLAlchemy,
    обернутых в более общие исключения.

    Args:
        exc: Исключение верхнего уровня, например `IntegrityError`.
        reason: Тип или кортеж типов ошибок, по которым нужно распознать причину (например, `UniqueViolationError`).
        to_raise: Исключение, которое будет выброшено, если причина найдена.

    Raises:
        to_raise: Если во вложенной цепочке `__cause__` найдена ошибка типа `reason`.
    """

    def walk_causes(err: BaseException | None) -> bool:
        seen = set()
        while err and err not in seen:
            if isinstance(err, reason):
                return True
            seen.add(err)
            err = getattr(err, "__cause__", None)
        return False

    orig = getattr(exc, "orig", None)
    if walk_causes(orig):
        raise to_raise()

    #
    # # # new_case: Так можно безопасно доставать вложеные(обернутые ошибки)
    # cause = getattr(exc.orig, "__cause__",
    #                 None)  # new_case: безопасная проверка что атрибут есть ex.orig.__cause__
    # if isinstance(exc.orig, UniqueViolationError) or isinstance(cause,
    #                                                             UniqueViolationError):  # new_case: вместо cause можно ex.orig.__cause__ но это не безопасный доступ
    #     raise ObjectAlreadyExistsException
    #
    # logging.error(f"Вывод exc: {type(exc).__name__}: {exc}")
    # logging.error("------------------------------------------------------")
    # logging.error(f"Вывод exc.orig: {type(exc).__name__}: {exc.orig}")
    # logging.error("------------------------------------------------------")
    # logging.error(f"Вывод exc.__context__: {type(exc).__name__}: {exc.__context__}")
    # logging.error("------------------------------------------------------")
    # logging.error(f"Вывод exc.__cause__: {type(exc).__name__}: {exc.__cause__}")
    # logging.error("------------------------------------------------------")
    # logging.error(f"Вывод exc.orig.__cause__: {type(exc).__name__}: {exc.orig.__cause__}")
