import dataclasses
import datetime
import json
from asyncpg import Connection


from ...db_exceptions import DbException


@dataclasses.dataclass
class UsedAsset():
    id: int
    user_id: int
    asset_id: int
    properties: dict
    created_at: datetime.datetime

    @classmethod
    def from_row(cls, row):
        _id, user_id, asset_id, properties, created_at = tuple(row)
        return cls(
            id=_id,
            user_id=user_id,
            asset_id=asset_id,
            properties=json.loads(properties),
            created_at=created_at,
        )

class UsedAssetsFunctions:
    def __init__(self, conn: Connection):
        self.conn = conn

    async def create_used_asset(self, user_id: int, asset_id: int, properties: dict) -> UsedAsset:
        res = await self.conn.fetchrow(
            """
            INSERT INTO used_assets (user_id, asset_id, properties)
            VALUES ($1, $2, $3)
            RETURNING *
            """,
            user_id,
            asset_id,
            json.dumps(properties),
        )
        return UsedAsset.from_row(res)

    async def get_used_assets_by_user(self, user_id: int):
        rows = await self.conn.fetch(
            "SELECT * FROM used_assets WHERE user_id = $1",
            user_id,
        )
        return [UsedAsset.from_row(row) for row in rows]

    async def delete_used_asset(self, asset_id: int):
        await self.conn.execute(
            "DELETE FROM used_assets WHERE id = $1",
            asset_id,
        )
