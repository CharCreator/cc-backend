import pydantic
import typing
import fastapi


class ErrorModel(pydantic.BaseModel):
    """
    Модель ошибки
    """

    code: int = pydantic.Field(..., description="Код ошибки", title="Код")
    message: str = pydantic.Field(
        ..., description="Сообщение об ошибке", title="Сообщение"
    )
    fields: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        None, description="Словарь с подробным описанием ошибки", title="Поля"
    )

    # TODO: include exception fields
    def as_http_exception(
        self,
        detail: typing.Any = None,
        remove_cookies: typing.Optional[typing.List[str]] = None,
    ):
        detail = detail or self.message
        full_detail = {"message": detail, "fields": {}}
        if self.fields:
            full_detail["fields"] = self.fields

        exception = fastapi.HTTPException(
            status_code=self.code,
            detail=full_detail,
        )
        exception.custom_data = self
        exception.remove_cookies = remove_cookies
        return exception

    def __str__(self):
        field_details = ", ".join(
            [f"{key}: {value}" for key, value in (self.fields or {}).items()]
        )
        return f'Code {self.code}: "{self.message}". Fields: {field_details}'


class UserModel(pydantic.BaseModel):
    """
    Модель пользователя
    """

    id: int = pydantic.Field(..., description="Идентификатор пользователя", title="ID")
    email: str = pydantic.Field(..., description="Email пользователя", title="Email")
    email_verified: bool = pydantic.Field(
        ..., description="Подтвержден ли email", title="Email подтвержден"
    )
    admin_level: int = pydantic.Field(
        ..., description="Уровень администратора", title="Уровень администратора"
    )




class ExceptionModel(pydantic.BaseModel):
    """
    Модель исключения
    """

    code: int = pydantic.Field(..., description="Код ошибки", title="Код")
    message: str = pydantic.Field(
        ..., description="Сообщение об ошибке", title="Сообщение"
    )
    fields: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        None, description="Словарь с подробным описанием ошибки", title="Поля"
    )
    exception: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        None, description="Словарь с подробным описанием ошибки", title="Поля"
    )

    def as_http_exception(
        self,
        detail: typing.Any = None,
        remove_cookies: typing.Optional[typing.List[str]] = None,
    ):
        from ..config import Config

        config = Config()
        if config.is_production:
            detail = None
        else:
            detail = detail or self.message
        exception = fastapi.HTTPException(
            status_code=self.code,
            detail=detail or self.message,
        )
        exception.custom_data = self
        exception.remove_cookies = remove_cookies
        return exception
