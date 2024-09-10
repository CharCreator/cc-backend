import dataclasses
import datetime
import enum
import typing
import uuid

import asyncpg
from asyncpg import Connection

from ...db_exceptions import DbException
from ....shared_models import UserModel


class CodePurpose(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


@dataclasses.dataclass(frozen=True)
class Code:
    id: int
    user_id: int
    purpose: CodePurpose
    code: str
    created_at: datetime.datetime
    used_at: typing.Optional[datetime.datetime]
    expires_at: typing.Optional[datetime.datetime]

    @classmethod
    def from_row(cls, row):
        id_, user_id, purpose, code, created_at, used_at, expires_at = tuple(row)

        return cls(
            id=id_,
            user_id=user_id,
            purpose=CodePurpose(purpose),
            code=code,
            created_at=created_at,
            used_at=used_at,
            expires_at=expires_at,
        )


class CodeFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn

    async def create_code(
        self,
        user_id: int,
        purpose: CodePurpose,
        expires_at: datetime.datetime,
        code: typing.Optional[str] = None,
    ) -> Code:
        """
        Inserts a new code into the database

        :param user_id: id of the user, for whom the code is created
        :param purpose: purpose of the code
        :param expires_at: datetime when the code expires
        :param code: code to use, if None, a new code will be generated
        :return: newly created code
        """
        if code is None:
            code = str(uuid.uuid4())

        res = await self.conn.fetchrow(
            "INSERT INTO codes (user_id, purpose, code, expires_at) "
            "VALUES ($1, $2, $3, $4) RETURNING *",
            user_id,
            purpose.value,
            code,
            expires_at,
        )

        return Code.from_row(res)

    async def get_code(self, code: str) -> typing.Optional[Code]:
        """
        Fetches a code by the code string

        :param code: code string
        :return: Code or None
        """
        res = await self.conn.fetchrow(
            "SELECT * FROM codes WHERE code = $1",
            code,
        )

        if res is None:
            return None

        return Code.from_row(res)

    async def last_code_of_user(
        self, user_id: int, purpose: typing.Optional[CodePurpose] = None
    ) -> typing.Optional[Code]:
        """
        Fetches the last code of the user by the purpose

        :param user_id: id of the user
        :param purpose: purpose of the code, None to fetch any purpose
        :return: Code or None
        """
        if purpose is None:
            res = await self.conn.fetchrow(
                "SELECT * FROM codes WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1",
                user_id,
            )
        else:
            res = await self.conn.fetchrow(
                "SELECT * FROM codes WHERE user_id = $1 AND purpose = $2 ORDER BY created_at DESC LIMIT 1",
                user_id,
                purpose.value,
            )

        if res is None:
            return None

        return Code.from_row(res)

    async def get_and_mark_code_as_used(self, code: str) -> typing.Optional[Code]:
        """
        Fetches a code by the code string and marks it as used

        :param code: code string
        :return: Code or None
        """

        res = await self.conn.execute(
            "UPDATE codes SET used_at = NOW() WHERE id = $1 RETURNING *",
            code,
        )

        if res is None:
            return None

        return Code.from_row(res)

    async def mark_code_as_used(self, code_id: int | Code) -> None:
        """
        Marks a code as used

        :param code_id: id of the code or Code object
        """
        code_id = code_id.id if isinstance(code_id, Code) else code_id
        await self.conn.execute(
            "UPDATE codes SET used_at = NOW() WHERE id = $1",
            code_id,
        )
