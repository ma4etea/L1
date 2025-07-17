from datetime import date

from pydantic import BaseModel, model_validator, field_validator
from fastapi import HTTPException

class PatchValidatorMixin(BaseModel):
    """
    Миксин для Pydantic-моделей, предназначенных для PATCH-запросов.

    Цель миксина — гарантировать, что при частичном обновлении (PATCH)
    клиент передаёт хотя бы одно поле.

    Если в запросе не передано ни одного поля (модель пуста),
    будет выброшено исключение HTTP 422 с сообщением:

        "Нужно передать хотя бы одно поле"

    Это позволяет избежать бессмысленных PATCH-запросов без содержимого.

    Пример использования:

    ```python
    class EditRoom(PatchValidatorMixin):
        title: str = None
        description: str | None = None
    ```

    ```json
    {} # ❌ вызовет HTTPException 422
    {title="Новый заголовок"} # ✅ корректно
    {description="Новое описание"} # ✅ корректно
    ```

    Замечание:
    - Поля должны иметь значение по умолчанию `None`, чтобы быть опциональными.
    - Эта проверка выполняется после всех остальных валидаторов Pydantic.

    """

    @model_validator(mode="after")
    def at_least_one_non_null(self):
        data = self.model_dump(exclude_unset=True)

        if not data:
            raise HTTPException(
                status_code=422,
                detail="Нужно передать хотя бы одно поле",
            )
        return self


class DateRangeValidatorMixin(BaseModel):
    """
    Mixin-класс для валидации диапазона дат.

    Проверяет, что поле `date_from` строго меньше `date_to`.

    Требования:
        - Подключаемая модель должна иметь поля:
            - `date_from: date` дата заезда
            - `date_to: date`   дата выезда

    Исключения:
        - HTTPException 422, если `date_from >= date_to`
    """

    date_from: date
    date_to: date

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.date_from >= self.date_to:
            raise HTTPException(
                status_code=422,
                detail="`date_from` должно быть меньше `date_to`"
            )
        return self


class DateFromTodayOrLaterMixin(BaseModel):
    """
    Mixin-класс для валидации, что поле `date_from` установлено на сегодняшнюю дату
    или позже.

    Назначение:
        - Проверяет, что `date_from >= date.today()`

    Поведение:
        - Если `date_from` меньше сегодняшнего дня, выбрасывается HTTPException с кодом 422.

    Требования:
        - Подключаемая модель должна содержать поле:
            - `date_from: date`
    """

    @field_validator("date_from", check_fields=False)
    def must_be_today_or_later(cls, v: date) -> date:
        today = date.today()
        if v < today:
            raise HTTPException(
                status_code=422,
                detail=f"`date_from` не может быть в прошлом. Укажите сегодня или позже: {today.isoformat()}"
            )
        return v