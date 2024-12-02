import pydantic


class CharacterModel(pydantic.BaseModel):
    """
    Модель сохранённого персонажа
    """

    id: int = pydantic.Field(..., description="Идентификатор записи", title="ID")
    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя", title="ID пользователя"
    )
    name: str = pydantic.Field(
        ..., description="Имя персонажа", title="Имя персонажа"
    )
    created_at: str = pydantic.Field(
        ..., description="Дата и время создания записи в ISO 8601 формате", title="Дата создания"
    )
