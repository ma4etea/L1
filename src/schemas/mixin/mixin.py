from pydantic import BaseModel, model_validator
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
