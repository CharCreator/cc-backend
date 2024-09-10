import asyncio
import dataclasses
import time
import typing
import datetime

from asyncpg import Connection, PostgresError, Record

from ...db_exceptions import DbException


@dataclasses.dataclass(frozen=True)
class Session:
    id: int
    user_id: int
    token: str
    created_at: datetime.datetime
    last_used: datetime.datetime
    expires_at: datetime.datetime

    @classmethod
    def from_row(cls, row):
        (
            id_,
            user_id,
            token,
            created_at,
            last_used,
            expires_at,
        ) = tuple(row)

        return cls(
            id=id_,
            user_id=user_id,
            token=token,
            created_at=created_at,
            last_used=last_used,
            expires_at=expires_at,
        )

    @property
    def expired(self):
        return self.expires_at < datetime.datetime.now()


class SessionsFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn

    async def create(
        self, user_id: int, token: str, expires_at: datetime.datetime
    ) -> Session:
        """
        Creates a new session

        :param user_id: id of the user
        :param token: JWT token
        :param expires_at: datetime when the token will expire
        :return: a new session
        """

        record = await self.conn.fetchrow(
            "INSERT INTO sessions(user_id, token, expires_at) VALUES ($1, $2, $3) RETURNING *",
            user_id,
            token,
            expires_at,
        )
        return Session.from_row(record)

    async def get(self, token: str, update=True) -> typing.Optional[Session]:
        """
        Retrieves a session by token

        :param token: JWT token
        :param update: whether to update the last_used field
        :return: a session
        """
        if update:
            record = await self.conn.fetchrow(
                "UPDATE sessions SET last_used = NOW() WHERE token = $1 RETURNING *",
                token,
            )
        else:
            record = await self.conn.fetchrow(
                "SELECT * FROM sessions WHERE token = $1",
                token,
            )

        return Session.from_row(record) if record else None

    async def delete(self, token: str):
        """
        Deletes a session by token

        :param token: JWT token
        :return: None
        """
        await self.conn.execute("DELETE FROM sessions WHERE token = $1", token)

    async def delete_by_id(self, session_id: int | Session):
        """
        Deletes a session by id

        :param session_id: session id
        :return: None
        """
        session_id = session_id.id if isinstance(session_id, Session) else session_id

        await self.conn.execute("DELETE FROM sessions WHERE id = $1", session_id)

    async def delete_all_sessions_except(
        self,
        session: Session,
    ):
        """
        Deletes all sessions except the current one

        :param session: current session
        :return: None
        """
        await self.conn.execute(
            "DELETE FROM sessions WHERE user_id = $1 AND id != $2",
            session.user_id,
            session.id,
        )
