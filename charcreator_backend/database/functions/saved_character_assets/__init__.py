import asyncio
import dataclasses
import time
import typing
from enum import Enum

from asyncpg import Connection, PostgresError, Record

from ...db_exceptions import DbException
