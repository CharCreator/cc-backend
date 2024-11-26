import dataclasses
import datetime
import typing

import asyncpg
from asyncpg import Connection

from ...db_exceptions import DbException
from ....shared_models import SavedCharacterModel


@dataclasses.dataclass(frozen=True)
class SavedCharacter:
    id: int
    user_id: int
    name: str
    created_at: datetime.datetime

    @classmethod
    def from_row(cls, row):
        id_, user_id, name, created_at = tuple(row)
        return cls(
            id=id_,
            user_id=user_id,
            name=name,
            created_at=created_at,
        )

    def to_model(self):
        return SavedCharacterModel(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            created_at=self.created_at.isoformat(),
        )


class SavedCharacterNotFound(DbException):
    pass


class SavedCharacterFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn

    async def create_saved_character(
        self, user_id: int, name: str
    ) -> SavedCharacter:
        """
        Create a new saved character
        :param user_id: ID of the user
        :param name: Name of the character
        :return: A newly created SavedCharacter object
        """
        res = await self.conn.fetchrow(
            """
            INSERT INTO saved_characters (user_id, name, created_at) 
            VALUES ($1, $2, NOW()) RETURNING *
            """,
            user_id,
            name,
        )
        return SavedCharacter.from_row(res)

    async def get_by_id(self, saved_character_id: int) -> typing.Optional[SavedCharacterModel]:
        """
        Retrieve a saved character by its ID
        :param saved_character_id: ID of the saved character
        :return: SavedCharacterModel or None
        """
        res = await self.conn.fetchrow(
            "SELECT * FROM saved_characters WHERE id = $1",
            saved_character_id,
        )
        if res is None:
            raise SavedCharacterNotFound()
        return SavedCharacter.from_row(res).to_model()

    async def get_all_by_user(self, user_id: int) -> typing.List[SavedCharacterModel]:
        """
        Retrieve all saved characters by a user
        :param user_id: ID of the user
        :return: List of SavedCharacterModel
        """
        rows = await self.conn.fetch(
            "SELECT * FROM saved_characters WHERE user_id = $1",
            user_id,
        )
        return [SavedCharacter.from_row(row).to_model() for row in rows]

    async def update_name(self, saved_character_id: int, name: str) -> SavedCharacterModel:
        """
        Update the name of a saved character
        :param saved_character_id: ID of the saved character
        :param name: New name
        :return: Updated SavedCharacterModel
        :raises: SavedCharacterNotFound
        """
        res = await self.conn.fetchrow(
            """
            UPDATE saved_characters 
            SET name = $2 
            WHERE id = $1 RETURNING *
            """,
            saved_character_id,
            name,
        )
        if res is None:
            raise SavedCharacterNotFound()
        return SavedCharacter.from_row(res).to_model()

    async def delete(self, saved_character_id: int):
        """
        Delete a saved character by its ID
        :param saved_character_id: ID of the saved character
        :raises: SavedCharacterNotFound
        """
        res = await self.conn.execute(
            "DELETE FROM saved_characters WHERE id = $1",
            saved_character_id,
        )
        if res == "DELETE 0":
            raise SavedCharacterNotFound()
