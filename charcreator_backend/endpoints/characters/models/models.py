import datetime
import pydantic


class ModifyCharacterRequest(pydantic.BaseModel):
    """
    Модель для запроса на создание или обновление сохранённого персонажа.
    """

    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя, для которого создаётся или обновляется персонаж", title="User ID", ge=0
    )
    name: str = pydantic.Field(
        ..., description="Имя персонажа", title="Name", max_length=255
    )

class GetAllCharactersRequest(pydantic.BaseModel):
    """
    Модель запроса для получения списка персонажей пользователя.
    """

    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя, чьи персонажи запрашиваются", title="User ID", ge=0
    )


class GetCharacterResponse(pydantic.BaseModel):
    """
    Модель для ответа при запросе информации о сохранённом персонаже.
    """

    id: int = pydantic.Field(
        ..., description="Уникальный идентификатор сохранённого персонажа", title="ID", ge=0
    )
    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя, которому принадлежит персонаж", title="User ID", ge=0
    )
    name: str = pydantic.Field(
        ..., description="Имя персонажа", title="Name", max_length=255
    )
    created_at: datetime.datetime = pydantic.Field(
        ..., description="Дата и время создания персонажа", title="Creation Date"
    )
