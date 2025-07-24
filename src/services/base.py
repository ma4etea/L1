import logging
import math

from src.exceptions.exсeptions import (
    PageNotFoundException,
    InvalidPaginationException,
    ObjectNotFoundException,
)
from src.utils.db_manager import DBManager


# todo возможно для супер продакшен реди, нужно в сервис передовать дата классы или дикт а не педантик схемы(в сервисе должен быть только пайтон)
class BaseService:
    db: DBManager | None

    def __init__(self, db: DBManager | None = None):
        self.db = db

    def get_pagination_with_check(
        self, page: int, per_page: int, check_total: int = None
    ) -> tuple[int, int]:
        """
        Проверяет параметры пагинации и возвращает offset и limit.

        Args:
            page (int): Номер страницы (начиная с 1).
            per_page (int): Количество элементов на странице.
            check_total (int, optional): Общее количество элементов (например, из COUNT(*)).
                Если передано и offset выходит за пределы total, выбрасывается исключение PageNotFoundException.

        Returns:
            tuple[int, int]: Кортеж из двух значений:
                - offset (int): Смещение (количество пропущенных элементов).
                - limit (int): Количество элементов на странице.

        Raises:
            InvalidPaginationException: Если `page` или `per_page` меньше 1.
            PageNotFoundException: Если `offset >= check_total` (и `check_total` задан), то есть страница выходит за пределы.

        Пример:
            self.check_pagination(page=2, per_page=10, check_total=35)
            (10, 10)
        """
        offset = per_page * page - per_page
        limit = per_page
        if per_page < 1 or page < 1:
            logging.warning(f"Неверные данные пагинации{page=}{per_page=}")
            raise InvalidPaginationException
        if check_total is not None and offset >= check_total:
            if check_total <= 0:
                raise ObjectNotFoundException
            page = max(1, math.ceil(check_total / per_page))
            raise PageNotFoundException(details=f"Максимум доступна {page=}")

        return offset, limit
