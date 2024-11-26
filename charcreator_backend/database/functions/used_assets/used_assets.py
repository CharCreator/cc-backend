import dataclasses
import datetime
import typing
import json
import asyncpg
from asyncpg import Connection

from ...db_exceptions import DbException
from ....shared_models import UsedAssetModel


@dataclasses.dataclass(frozen=True)
class UsedAsset:
    id: int
    user_id: int
    asset_id: int
    properties: dict[str, typing.Any]
    created_at: str

    @classmethod
    def from_row(cls, row):
        id_, user_id, asset_id, properties, created_at = tuple(row)
        return cls(
            id=id_,
            user_id=user_id,
            asset_id=asset_id,
            properties=properties,
            created_at=created_at,
        )

    def to_model(self):
        return UsedAssetModel(
            id=self.id,
            user_id=self.user_id,
            asset_id=self.asset_id,
            properties=self.properties,
            created_at=self.created_at,
        )


class UsedAssetNotFound(DbException):
    pass


class UsedAssetFunctions:
    def __init__(self, conn):
        self.conn: Connection = conn

    async def create_used_asset(
        self, user_id: int, asset_id: int, properties: dict
    ) -> UsedAsset:
        """
        Create a new used asset
        :param user_id: ID of the user
        :param asset_id: ID of the asset
        :param properties: Additional properties as a dictionary
        :return: A newly created UsedAsset object
        """
        res = await self.conn.fetchrow(
            """
            INSERT INTO used_assets (user_id, asset_id, properties, created_at) 
            VALUES ($1, $2, $3, NOW()) RETURNING *
            """,
            user_id,
            asset_id,
            json.dump(properties),
        )
        return UsedAsset.from_row(res)

    async def get_by_id(self, used_asset_id: int) -> typing.Optional[UsedAssetModel]:
        """
        Retrieve a used asset by its ID
        :param used_asset_id: ID of the used asset
        :return: UsedAssetModel or None
        """
        res = await self.conn.fetchrow(
            "SELECT * FROM used_assets WHERE id = $1",
            used_asset_id,
        )
        if res is None:
            raise UsedAssetNotFound()
        return UsedAsset.from_row(res).to_model()

    async def get_all_by_user(self, user_id: int) -> typing.List[UsedAssetModel]:
        """
        Retrieve all used assets by a user
        :param user_id: ID of the user
        :return: List of UsedAssetModel
        """
        rows = await self.conn.fetch(
            "SELECT * FROM used_assets WHERE user_id = $1",
            user_id,
        )
        return {UsedAsset.from_row(row).to_model() for row in rows}

    async def update_properties(self, used_asset_id: int, properties: dict) -> UsedAssetModel:
        """
        Update the properties of a used asset
        :param used_asset_id: ID of the used asset
        :param properties: New properties
        :return: Updated UsedAssetModel
        :raises: UsedAssetNotFound
        """
        res = await self.conn.fetchrow(
            """
            UPDATE used_assets 
            SET properties = $2 
            WHERE id = $1 RETURNING *
            """,
            used_asset_id,
            properties,
        )
        if res is None:
            raise UsedAssetNotFound()
        return UsedAsset.from_row(res).to_model()

    async def delete(self, used_asset_id: int):
        """
        Delete a used asset by its ID
        :param used_asset_id: ID of the used asset
        :raises: UsedAssetNotFound
        """
        res = await self.conn.execute(
            "DELETE FROM used_assets WHERE id = $1",
            used_asset_id,
        )
        if res == "DELETE 0":
            raise UsedAssetNotFound()
