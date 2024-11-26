import datetime
import pydantic


class SavedCharacterRequest(pydantic.BaseModel):
    """
    Модель запроса для создания или обновления сохранённого персонажа
    """

    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя", title="User ID", ge=0
    )
    name: str = pydantic.Field(
        ..., description="Имя персонажа", title="Name", max_length=255
    )


class SavedCharacterResponse(pydantic.BaseModel):
    """
    Модель ответа для сохранённого персонажа
    """

    id: int = pydantic.Field(
        ..., description="Идентификатор сохранённого персонажа", title="ID", ge=0
    )
    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя", title="User ID", ge=0
    )
    name: str = pydantic.Field(
        ..., description="Имя персонажа", title="Name", max_length=255
    )
    created_at: datetime.datetime = pydantic.Field(
        ..., description="Дата создания", title="Дата создания"
    )
