import datetime
import pydantic


class SavedCharacterAssetRequest(pydantic.BaseModel):
    """
    Модель запроса для создания или обновления связки персонажа и ассета
    """

    saved_character_id: int = pydantic.Field(
        ..., description="Идентификатор сохранённого персонажа", title="Saved Character ID", ge=0
    )
    used_asset_id: int = pydantic.Field(
        ..., description="Идентификатор использованного ассета", title="Used Asset ID", ge=0
    )


class SavedCharacterAssetResponse(pydantic.BaseModel):
    """
    Модель ответа для связки сохранённого персонажа и ассета
    """

    id: int = pydantic.Field(
        ..., description="Идентификатор связки", title="ID", ge=0
    )
    saved_character_id: int = pydantic.Field(
        ..., description="Идентификатор сохранённого персонажа", title="Saved Character ID", ge=0
    )
    used_asset_id: int = pydantic.Field(
        ..., description="Идентификатор использованного ассета", title="Used Asset ID", ge=0
    )
    created_at: datetime.datetime = pydantic.Field(
        ..., description="Дата создания", title="Дата создания"
    )
