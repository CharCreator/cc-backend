import pydantic
import datetime


class SavedCharacterAssetModel(pydantic.BaseModel):
    """
    Модель связи ассета с сохранённым персонажем
    """
    id: int = pydantic.Field(..., description="Идентификатор записи", title="ID")
    saved_character_id: int = pydantic.Field(
        ..., description="Идентификатор сохранённого персонажа", title="ID сохранённого персонажа"
    )
    used_asset_id: int = pydantic.Field(
        ..., description="Идентификатор использованного ассета", title="ID использованного ассета"
    )
    created_at: datetime.datetime = pydantic.Field(
        ...,
        description="Дата и время создания записи",
        title="Дата создания",
    )
