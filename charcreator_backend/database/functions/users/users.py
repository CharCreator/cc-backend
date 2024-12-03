import dataclasses
import datetime
import typing

import asyncpg
from asyncpg import Connection

from ...db_exceptions import DbException
from ....shared_models import UserModel

#Важно! Модифицируйте БД! Добавьте в таблицу users булевую колонку blocked, с дефолтом False. 
# У меня нет доступа к бд
# Вот SQL 
# ALTER TABLE users ADD COLUMN blocked BOOLEAN DEFAULT FALSE;
 

@dataclasses.dataclass(frozen=True)
class User:
    id: int
    email: str
    password_hash: str
    created_at: datetime.datetime
    email_verified: bool
    blocked: bool
    admin_level: int
    last_login: datetime.datetime

    @classmethod
    def from_row(cls, row):
        (
            id_,
            email,
            password_hash,
            created_at,
            email_verified,
            blocked,
            admin_level,
            last_login,
        ) = tuple(row)

        return cls(
            id=id_,
            email=email,
            password_hash=password_hash,
            created_at=created_at,
            email_verified=email_verified,
            blocked=blocked,
            admin_level=admin_level,
            last_login=last_login,
        )

    def to_model(self):
        return UserModel(
            id=self.id,
            email=self.email,
            email_verified=self.email_verified,
            admin_level=self.admin_level,
        )


class EmailTaken(DbException):
    pass


class UserNotFound(DbException):
    pass


class UserNotFoundOrCredentialsInvalid(DbException):
    pass


class UserFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn

    async def signup_create_user(
        self,
        email: str,
        password_hash: str,
    ) -> User:
        """
        Create a new unverified user

        :param email: new user's email
        :param password_hash: bcrypt-hashed password
        :return: A newly created User object
        :raises: EmailTaken if email is already taken
        """

        try:
            res = await self.conn.fetchrow(
                "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING *",
                email,
                password_hash,
            )
        except asyncpg.UniqueViolationError as e:
            if "email" in str(e):
                raise EmailTaken()
            raise
        return User.from_row(res)

    async def mark_verified_email(self, user: int | User) -> User:
        """
        Set user's email_verified to True
        :param user: int, User - user to mark
        :return: User
        :raises: UserNotFound
        """

        user = user.id if isinstance(user, User) else user

        res = await self.conn.fetchrow(
            "UPDATE users SET email_verified = TRUE WHERE id = $1 RETURNING *", user
        )

        if res is None:
            raise UserNotFound()

        return User.from_row(res)

    async def verify_password(self, email, password_hash) -> User:
        """
        Verify user's password
        :param email: user's email
        :param password_hash: bcrypt-hashed password
        :return: User
        :raises: UserNotFoundOrCredentialsInvalid
        """

        res = await self.conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND password_hash = $2",
            email,
            password_hash,
        )

        if res is None:
            raise UserNotFoundOrCredentialsInvalid()

        return User.from_row(res)

    async def get_user_by_email(self, email: str) -> typing.Optional[User]:
        """
        Get user by email
        :param email: user's email
        :return: User
        """

        res = await self.conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email,
        )

        return User.from_row(res)

    async def get(self, user: int | User) -> typing.Optional[User]:
        """
        Get user by id or User object
        :param user: user's id or User object
        :return: User or None
        """

        user = user.id if isinstance(user, User) else user

        res = await self.conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user,
        )

        if res is None:
            return None

        return User.from_row(res)

    async def update_last_login(self, user: int | User) -> User:
        """
        Update user's last_login to current time
        :param user: int, User - user to update
        :return: User
        :raises: UserNotFound
        """
        user = user.id if isinstance(user, User) else user
        res = await self.conn.fetchrow(
            "UPDATE users SET last_login = NOW() WHERE id = $1 RETURNING *", user
        )

        if res is None:
            raise UserNotFound()

        return User.from_row(res)

    async def set_password(self, user: int | User, password_hash: str) -> User:
        """
        Update user's password
        :param user: int, User - user to update
        :param password_hash: new password hash
        :return: User
        :raises: UserNotFound
        """
        user = user.id if isinstance(user, User) else user
        res = await self.conn.fetchrow(
            "UPDATE users SET password_hash = $2 WHERE id = $1 RETURNING *",
            user,
            password_hash,
        )

        if res is None:
            raise UserNotFound()

        return User.from_row(res)

    async def get_all_users(self) -> typing.List[User]:
      
        rows = await self.conn.fetch("SELECT * FROM users")
        return [User.from_row(row) for row in rows]

    ##############################################
    #Я жестко запутался в структуре, честно говоря
    ##############################################

    async def block_user(self, user: int | User) -> User:
        """
        Block a user by setting 'blocked' to True
        :param user: int, User - user to block
        :return: User
        :raises: UserNotFound
        """
        user = user.id if isinstance(user, User) else user
        res = await self.conn.fetchrow(
            "UPDATE users SET blocked = TRUE WHERE id = $1 RETURNING *",
            user,
        )

        if res is None:
            raise UserNotFound()

        return User.from_row(res)

    async def unblock_user(self, user: int | User) -> User:
        """
        Unblock a user by setting 'blocked' to False
        :param user: int, User - user to unblock
        :return: User
        :raises: UserNotFound
        """
        user = user.id if isinstance(user, User) else user
        res = await self.conn.fetchrow(
            "UPDATE users SET blocked = FALSE WHERE id = $1 RETURNING *",
            user,
        )

        if res is None:
            raise UserNotFound()

        return User.from_row(res)

    async def is_user_blocked(self, user: int | User) -> bool:
        """
        Check if the user is blocked
        :param user: int, User - user to check
        :return: bool - True if blocked, False otherwise
        """
        user = user.id if isinstance(user, User) else user
        res = await self.conn.fetchval(
            "SELECT blocked FROM users WHERE id = $1",
            user,
        )

        if res is None:
            raise UserNotFound()

        return res

