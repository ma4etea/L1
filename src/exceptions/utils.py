import logging
from datetime import date
from typing import Type, Tuple, TypeVar

from src.exceptions.exсeptions import InvalidDateAfterDate
from src.utils.logger_utils import exc_log_string


def check_data_from_after_date_to_http_exc(date_from: date, date_to: date):
    if date_from <= date_to:
        raise InvalidDateAfterDate


T = TypeVar("T", bound=BaseException)


def is_raise(
    exc: Exception,
    reason: Type[BaseException] | Tuple[Type[BaseException], ...],
    to_raise: Type[T],
    *,
    check_message_contains: tuple[str, ...] | str | None = None,
) -> None:
    """
    Проверяет, было ли исходное исключение (`exc`) вызвано ошибкой заданного типа (`reason`)
    внутри цепочки исключений (`__cause__`) и что **все** подстроки из
    `check_message_contains` присутствуют в полном сообщении `exc`.
    Если да — выбрасывает новое исключение (`to_raise`).

    Args:
        exc: Исключение верхнего уровня.
        reason: Тип или кортеж типов ошибок для распознавания причины.
        to_raise: Исключение, которое будет выброшено.
        check_message_contains: Список подстрок | подстрока, которые все должны быть в сообщении ошибки.

    Raises:
        to_raise: Если условия совпадения выполнены.
    """

    if check_message_contains:
        if isinstance(check_message_contains, str):
            check_messages_ = {check_message_contains}
        elif isinstance(check_message_contains, tuple):
            check_messages_ = set(check_message_contains)
        else:
            raise TypeError(
                f"Ожидаем str или последовательность [str], получил {type(check_message_contains)}"
            )
        full_msg = str(exc).lower()
        # Проверяем, что все подстроки есть в сообщении (регистр не важен)
        if not all(sub.lower() in full_msg for sub in check_messages_):
            return  # Не все подстроки найдены — выходим

    def walk_causes(err: BaseException | None) -> bool:
        seen = set()
        while err and err not in seen:
            if isinstance(err, reason):
                return True
            seen.add(err)
            err = getattr(err, "__cause__", None)
        return False

    orig = getattr(exc, "orig", None)
    if isinstance(orig, reason) or walk_causes(orig):
        logging.warning(f"Отловлено исключение: {exc_log_string(exc)}")
        raise to_raise() from exc


# def is_raise(
#     exc: Exception,
#     reason: Type[BaseException] | Tuple[Type[BaseException], ...],
#     to_raise: Type[T],
#     *,
#     check_message_contains: str = None
# ) -> None:
#     """
#     Проверяет, было ли исходное исключение (`exc`) вызвано ошибкой заданного типа (`reason`)
#     внутри цепочки исключений (`__cause__`) и, если да — выбрасывает новое исключение (`to_raise`).
#
#     Дополнительно можно указать строку `check_message_contains` для проверки содержания текста ошибки.
#
#     Args:
#         exc: Исключение верхнего уровня, например `IntegrityError`.
#         reason: Тип или кортеж типов ошибок, по которым нужно распознать причину (например, `UniqueViolationError`).
#         to_raise: Исключение, которое будет выброшено, если причина найдена.
#         check_message_contains: Опциональная подстрока для проверки в тексте ошибки.
#
#     Raises:
#         to_raise: Если во вложенной цепочке `__cause__` найдена ошибка типа `reason`
#             и (если указано) текст ошибки содержит `check_message_contains`.
#     """
#
#     def walk_causes(err: BaseException | None) -> bool:
#         seen = set()
#         while err and err not in seen:
#             # Проверяем тип
#             if isinstance(err, reason):
#                 # Если есть дополнительная проверка по тексту — проверяем
#                 if check_message_contains:
#                     if check_message_contains.lower() in str(exc).lower():
#                         return True
#                 else:
#                     return True
#             seen.add(err)
#             err = getattr(err, "__cause__", None)
#         return False
#
#     orig = getattr(exc, "orig", None)
#     if (isinstance(orig, reason) and
#         (not check_message_contains or check_message_contains.lower() in str(orig).lower())) or walk_causes(orig):
#         logging.warning(f"Отловлено исключение: {exc_log_string(exc)}")
#         raise to_raise() from exc

# def is_raise(
#         exc: Exception,
#         reason: Type[BaseException] | Tuple[Type[BaseException], ...],
#         to_raise: Type[T]
# ) -> None:
#     """
#     Проверяет, было ли исходное исключение (`exc`) вызвано ошибкой заданного типа (`reason`)
#     внутри цепочки исключений (`__cause__`) и, если да — выбрасывает новое исключение (`to_raise`).
#
#     Полезно при анализе вложенных ошибок, например, при обработке IntegrityError от SQLAlchemy,
#     обернутых в более общие исключения.
#
#     Args:
#         exc: Исключение верхнего уровня, например `IntegrityError`.
#         reason: Тип или кортеж типов ошибок, по которым нужно распознать причину (например, `UniqueViolationError`).
#         to_raise: Исключение, которое будет выброшено, если причина найдена.
#
#     Raises:
#         to_raise: Если во вложенной цепочке `__cause__` найдена ошибка типа `reason`.
#     """
#
#     def walk_causes(err: BaseException | None) -> bool:
#         seen = set()
#         while err and err not in seen:
#             if isinstance(err, reason):
#                 return True
#             seen.add(err)
#             err = getattr(err, "__cause__", None)
#         return False
#
#     orig = getattr(exc, "orig", None)
#     if isinstance(orig, reason) or walk_causes(orig):
#         logging.warning(exc_log_string(exc))
#         raise to_raise() from exc


#
# # # new_case: Так можно безопасно доставать вложеные(обернутые ошибки)
# cause = getattr(exc.orig, "__cause__",
#                 None)  # new_case: безопасная проверка что атрибут есть ex.orig.__cause__
# if isinstance(exc.orig, UniqueViolationError) or isinstance(cause,
#                                                             UniqueViolationError):  # new_case: вместо cause можно ex.orig.__cause__ но это не безопасный доступ
#     raise ObjectAlreadyExistsException
#
# logging.error(f"Вывод exc: exc_log_string(exc)")
# logging.error("------------------------------------------------------")
# logging.error(f"Вывод exc.orig: {type(exc).__name__}: {exc.orig}")
# logging.error("------------------------------------------------------")
# logging.error(f"Вывод exc.__context__: {type(exc).__name__}: {exc.__context__}")
# logging.error("------------------------------------------------------")
# logging.error(f"Вывод exc.__cause__: {type(exc).__name__}: {exc.__cause__}")
# logging.error("------------------------------------------------------")
# logging.error(f"Вывод exc.orig.__cause__: {type(exc).__name__}: {exc.orig.__cause__}")
