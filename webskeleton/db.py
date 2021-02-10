from typing import Sequence

import asyncpg  # type: ignore
from box import Box  # type: ignore


from webskeleton.env import ENV

pool: asyncpg.pool.Pool


def _check_pool():
    if not pool:
        raise Exception("not connected")
    return


async def _adjust_asyncpg_json_conversion(con: asyncpg.Connection):
    import json

    await con.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    await con.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    return


def get_connect_args() -> dict:
    return {
        "user": ENV.PGUSER,
        "password": ENV.PGPASSWORD,
        "database": ENV.PGDB,
        "host": ENV.PGHOST,
    }


# public
async def connect():
    global pool
    pool = await asyncpg.create_pool(
        **get_connect_args(),
        init=_adjust_asyncpg_json_conversion,
    )
    return


def as_box(record: asyncpg.Record) -> Box:
    return Box(record.items())


async def fetch_all(sql: str, bindargs: Sequence = []):
    _check_pool()
    async with pool.acquire() as con:
        async with con.transaction():
            return await con.fetch(sql, *bindargs)
    return


async def fetch_val(sql: str, bindargs: Sequence = []):
    _check_pool()
    async with pool.acquire() as con:
        async with con.transaction():
            return await con.fetchval(sql, *bindargs)
    return


async def execute(sql: str, bindargs: Sequence = []):
    _check_pool()
    async with pool.acquire() as con:
        async with con.transaction():
            return await con.execute(sql, *bindargs)
    return
