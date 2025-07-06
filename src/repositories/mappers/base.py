from pydantic import BaseModel as BaseSchema
from typing import TypeVar

from src.database import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseSchema)


class DataMapper:
    model: type[ModelType] = None
    schema: type[SchemaType] = None

    @classmethod
    def to_domain(cls, model):
        return cls.schema.model_validate(model, from_attributes=True)

    @classmethod
    def to_persist(cls, schema: BaseSchema):
        return cls.model(**schema.model_dump())
