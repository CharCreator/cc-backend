import dataclasses
import datetime
import typing

import asyncpg
from asyncpg import Connection

from ...db_exceptions import DbException
from ....shared_models import SavedCharacterAssetModel


@dataclasses.dataclass(frozen=True)
class SavedCharacterAsset:
    id: int
    saved_character_id: int
    used_asset_id: int
    created_at: datetime.datetime

    @classmethod
    def from_row(cls, row):
        id_, saved_character_id, used_asset_id, created_at = tuple(row)
        return cls(
            id=id_,
            saved_character_id=saved_character_id,
            used_asset_id=used_asset_id,
            created_at=created_at,
        )

    def to_model(self):
        return SavedCharacterAssetModel(
            id=self.id,
            saved_character_id=self.saved_character_id,
            used_asset_id=self.used_asset_id,
            created_at=self.created_at,
        )


class SavedCharacterAssetNotFound(DbException):
    pass


class SavedCharacterAssetFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn

    async def create_charasset(
        self, saved_character_id: int, used_asset_id: int
    ) -> SavedCharacterAsset:
        """
        Create a new saved character asset
        :param saved_character_id: ID of the saved character
        :param used_asset_id: ID of the used asset
        :return: A newly created SavedCharacterAsset object
        """
        res = await self.conn.fetchrow(
            """
            INSERT INTO saved_character_assets (saved_character_id, used_asset_id, created_at) 
            VALUES ($1, $2, NOW()) RETURNING *
            """,
            saved_character_id,
            used_asset_id,
        )
        return SavedCharacterAsset.from_row(res)

    async def get_charasset(self, saved_character_asset_id: int) -> typing.Optional[SavedCharacterAssetModel]:
        """
        Retrieve a saved character asset by its ID
        :param saved_character_asset_id: ID of the saved character asset
        :return: SavedCharacterAssetModel or None
        """
        res = await self.conn.fetchrow(
            "SELECT * FROM saved_character_assets WHERE id = $1",
            saved_character_asset_id,
        )
        if res is None:
            raise SavedCharacterAssetNotFound()
        return SavedCharacterAsset.from_row(res).to_model()

    async def get_all_charassets(self, saved_character_id: int) -> typing.List[SavedCharacterAssetModel]:
        """
        Retrieve all saved character assets by saved character ID
        :param saved_character_id: ID of the saved character
        :return: List of SavedCharacterAssetModel
        """
        rows = await self.conn.fetch(
            "SELECT * FROM saved_character_assets WHERE saved_character_id = $1",
            saved_character_id,
        )
        return [SavedCharacterAsset.from_row(row).to_model() for row in rows]

    async def delete(self, saved_character_asset_id: int):
        """
        Delete a saved character asset by its ID
        :param saved_character_asset_id: ID of the saved character asset
        :raises: SavedCharacterAssetNotFound
        """
        res = await self.conn.execute(
            "DELETE FROM saved_character_assets WHERE id = $1",
            saved_character_asset_id,
        )
        if res == "DELETE 0":
            raise SavedCharacterAssetNotFound()
