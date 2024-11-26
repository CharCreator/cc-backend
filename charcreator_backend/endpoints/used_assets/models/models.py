import datetime
import typing
import pydantic


class UsedAssetRequest(pydantic.BaseModel):
    """
    Модель запроса для создания или обновления использованного ассета
    """

    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя", title="User ID", ge=0
    )
    asset_id: int = pydantic.Field(
        ..., description="Идентификатор ассета", title="Asset ID", ge=0
    )
    properties: dict[str, typing.Any] = pydantic.Field(
        ..., description="Свойства ассета в формате JSON", title="Properties", default_factory=dict
    )


class UsedAssetResponse(pydantic.BaseModel):
    """
    Модель ответа для использованного ассета
    """

    id: int = pydantic.Field(
        ..., description="Идентификатор использованного ассета", title="ID", ge=0
    )
    user_id: int = pydantic.Field(
        ..., description="Идентификатор пользователя", title="User ID", ge=0
    )
    asset_id: int = pydantic.Field(
        ..., description="Идентификатор ассета", title="Asset ID", ge=0
    )
    properties: dict[str, typing.Any] = pydantic.Field(
        ..., description="Свойства ассета в формате JSON", title="Properties", default_factory=dict
    )
    created_at: datetime.datetime = pydantic.Field(
        ..., description="Дата создания", title="Дата создания"
    )

    class Config:
        # Это будет использовать стандартный формат ISO 8601 для datetime
        # (например, "2024-11-26T15:30:45.123456")
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()  # преобразует datetime в строку
        }
