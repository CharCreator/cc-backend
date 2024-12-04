import datetime
import pydantic
import typing


class GetAllAssetsRequest(pydantic.BaseModel):
    """
    Модель для запроса списка ассетов, связанных с персонажем пользователя.
    """

    character_id: int = pydantic.Field(
        ..., description="Идентификатор персонажа, для которого запрашиваются ассеты", title="Character ID", ge=0
    )


class ModifyCharAssetRequest(pydantic.BaseModel):
    """
    Модель запроса для создания или обновления ассоциации между персонажем и ассетом.
    """

    saved_character_id: int = pydantic.Field(
        ..., description="Идентификатор персонажа, чьи данные сохраняются", title="Saved Character ID", ge=0
    )
    used_asset_id: int = pydantic.Field(
        ..., description="Идентификатор ассета, который используется персонажем", title="Used Asset ID", ge=0
    )


class GetCharAssetResponse(pydantic.BaseModel):
    """
    Модель ответа для получения информации о связке персонажа и ассета.
    """

    id: int = pydantic.Field(
        ..., description="Уникальный идентификатор связки", title="ID", ge=0
    )
    saved_character_id: int = pydantic.Field(
        ..., description="Идентификатор сохранённого персонажа", title="Saved Character ID", ge=0
    )
    used_asset_id: int = pydantic.Field(
        ..., description="Идентификатор используемого ассета", title="Used Asset ID", ge=0
    )
    created_at: datetime.datetime = pydantic.Field(
        ..., description="Дата и время создания записи", title="Дата создания"
    )
