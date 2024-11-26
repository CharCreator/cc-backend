import asyncpg
from asyncpg import transaction
from ..config import Config
from .functions import (
    codes,
    users,
    assets,
    used_assets,
    saved_character_assets,
    saved_characters,
    sessions,
)

class FunctionsNamespace:
    def __init__(self, connection: asyncpg.connection.Connection):
        self.connection = connection
        self.users: users.UserFunctions = users.UserFunctions(connection)
        self.codes: codes.CodeFunctions = codes.CodeFunctions(connection)
        self.used_assets: used_assets.UsedAssetFunctions = used_assets.UsedAssetFunctions(connection)  # Исправлено имя класса
        self.saved_character_assets: saved_character_assets.SavedCharacterAssetFunctions = saved_character_assets.SavedCharacterAssetFunctions(connection)
        self.saved_characters: saved_characters.SavedCharacterFunctions = saved_characters.SavedCharacterFunctions(connection)
        self.sessions: sessions.SessionsFunctions = sessions.SessionsFunctions(connection)



class DBPool:
    _instance = None

    @staticmethod
    async def get_instance(no_save=False):
        config = Config()
        if no_save:
            return await asyncpg.create_pool(
                user=config.db.user,
                password=config.db.password,
                database=config.db.database,
                host=config.db.host,
            )
        if DBPool._instance is None:
            DBPool._instance = await asyncpg.create_pool(
                user=config.db.user,
                password=config.db.password,
                database=config.db.database,
                host=config.db.host,
            )
        return DBPool._instance


class TransactionManager:
    pool: asyncpg.pool.Pool
    conn: asyncpg.connection.Connection
    tran: asyncpg.transaction.Transaction
    functions: FunctionsNamespace

    def __init__(self, no_save=False):
        self.explicit_rollback = False
        self.no_save = no_save

    async def __aenter__(self):
        self.pool = await DBPool.get_instance(self.no_save)
        self.conn = await self.pool.acquire()
        self.tran = self.conn.transaction()
        await self.tran.start()
        self.functions = FunctionsNamespace(self.conn)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type or self.explicit_rollback:
                await self.tran.rollback()
            else:
                await self.tran.commit()
        finally:
            await self.pool.release(self.conn)

    async def rollback(self):
        if self.tran:
            await self.tran.rollback()
            self.explicit_rollback = True
