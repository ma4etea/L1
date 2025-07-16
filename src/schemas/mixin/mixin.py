from pydantic import BaseModel, model_validator
from fastapi import HTTPException

class PatchValidatorMixin(BaseModel):
    @model_validator(mode="after")
    def at_least_one_non_null(self):
        data = self.model_dump(exclude_unset=True)

        if not data:
            raise HTTPException(
                status_code=422,
                detail="Нужно передать хотя бы одно поле",
            )
        if all(value is None for value in data.values()):
            fields = ", ".join(data.keys())
            raise HTTPException(
                status_code=422,
                detail=f"Поля [{fields}] не могут быть одновременно null",
            )
        return self

class RemoveNullFieldsMixin(BaseModel):
    @model_validator(mode="before")
    def remove_null_fields(cls, data):
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data

class RejectNullFieldsMixin(BaseModel):
    @model_validator(mode="before")
    def reject_nulls(cls, data):
        if isinstance(data, dict):
            null_fields = [key for key, value in data.items() if value is None]
            if null_fields:
                fields = ", ".join(null_fields)
                raise HTTPException(
                    status_code=422,
                    detail=f"Поля [{fields}] не могут быть null",
                )
        return data