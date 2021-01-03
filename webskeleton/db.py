from typing import List

import asyncpg


pool: asyncpg.pool.Pool


def _check_pool():
    if not pool:
        raise Exception("not connected")
    return


async def _adjust_asyncpg_json_conversion(con: asyncpg.Connection):
    import json
    await con.set_type_codec(
        'jsonb',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )
    await con.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )
    return


async def connect(
        user: str = "postgres",
        password: str = "",
        database: str = "postgres",
        host: str = "127.0.0.1",
):
    global pool
    pool = await asyncpg.create_pool(
        user=user,
        password=password,
        database=database,
        host=host,
        init=_adjust_asyncpg_json_conversion,
    )
    return


async def fetch_all(sql: str, bindargs: List = []):
    _check_pool()
    async with pool.acquire() as con:
        async with con.transaction():
            return await con.fetch(sql, *bindargs)
    return


async def fetch_val(sql: str, bindargs: List = []):
    _check_pool()
    async with pool.acquire() as con:
        async with con.transaction():
            return await con.fetchval(sql, *bindargs)
    return


async def execute(sql: str, bindargs: List = []):
    _check_pool()
    async with pool.acquire() as con:
        async with con.transaction():
            return await con.execute(sql, *bindargs)
    return
