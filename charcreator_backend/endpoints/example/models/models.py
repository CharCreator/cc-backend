import datetime
import typing

import pydantic


class ExampleRequest(pydantic.BaseModel):
    """
    Модель запроса для примера
    """

    id: int = pydantic.Field(..., description="Идентификатор", title="ID", ge=0, le=1000)
    name: str = pydantic.Field(..., description="Имя", title="Имя", max_length=100)
    description: str = pydantic.Field(
        ..., description="Описание", title="Описание", max_length=1000
    )
    tags: typing.List[str] = pydantic.Field(
        ..., description="Теги", title="Теги", max_items=10
    )

class ExampleResponse(pydantic.BaseModel):
    """
    Модель ответа для примера
    """

    id: int = pydantic.Field(..., description="Идентификатор", title="ID", ge=0, le=1000)
    name: str = pydantic.Field(..., description="Имя", title="Имя", max_length=100)
    description: str = pydantic.Field(
        ..., description="Описание", title="Описание", max_length=1000
    )
    tags: typing.List[str] = pydantic.Field(
        ..., description="Теги", title="Теги", max_items=10
    )
    created_at: datetime.datetime = pydantic.Field(
        ..., description="Дата создания", title="Дата создания"
    )
    updated_at: datetime.datetime = pydantic.Field(
        ..., description="Дата обновления", title="Дата обновления"
    )
