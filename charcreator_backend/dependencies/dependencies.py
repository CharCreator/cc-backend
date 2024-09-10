import typing

import fastapi

from ..database import TransactionManager, functions
from ..shared_models import ErrorModel


class SessionData:
    session: functions.sessions.Session
    user: functions.users.User

    def __init__(self, session: functions.sessions.Session, user: functions.users.User):
        self.session = session
        self.user = user


async def may_be_logged_in(
    authorization: str = fastapi.Cookie(None, title="Токен авторизации"),
) -> typing.Optional[SessionData]:
    """
    Get current user

    :param authorization: cookie with authorization token
    :return: user information
    """
    if authorization is None:
        return None

    async with TransactionManager() as transaction_manager:
        session = await transaction_manager.functions.sessions.get(authorization)
        if not session or session.expired:
            return None

        user = await transaction_manager.functions.users.get(session.user_id)
        return SessionData(session, user)


async def must_be_logged_in(
    authorization: str = fastapi.Cookie(None, title="Токен авторизации"),
) -> SessionData:
    """
    Get current user

    :param authorization: cookie with authorization token
    :return: user information
    :raise: ErrorModel(code=status.HTTP_401_UNAUTHORIZED) if user is not authorized
    """
    data = await may_be_logged_in(authorization)
    if data is None:
        raise ErrorModel(
            code=fastapi.status.HTTP_401_UNAUTHORIZED,
            message="You must be logged in",
        ).as_http_exception()
    return data


async def local_request(
    request: fastapi.Request,
):
    client_host = request.headers.get("X-Real-IP", request.client[0])
    if client_host not in ["localhost", "127.0.0.1", "testclient"]:
        raise ErrorModel(
            code=fastapi.status.HTTP_403_FORBIDDEN,
            message="You are not allowed to perform this action",
        ).as_http_exception()
