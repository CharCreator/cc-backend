import pydantic
import typing



class UsedAssetModel(pydantic.BaseModel):
    """
    Модель использованного ассета
    """

    id: int = pydantic.Field(..., description="Идентификатор записи", title="ID")
    user_id: int = pydantic.Field(..., description="Идентификатор пользователя", title="ID пользователя")
    asset_id: int = pydantic.Field(..., description="Идентификатор ассета", title="ID ассета")
    properties: typing.Dict[str, typing.Any] = pydantic.Field(
        default_factory=dict,
        description="Свойства ассета в формате JSON",
        title="Свойства ассета"
    )
    created_at: str = pydantic.Field(
        ...,
        description="Дата и время создания записи в ISO 8601 формате",
        title="Дата создания"
    )