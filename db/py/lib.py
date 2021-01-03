import asyncpg


async def adjust_asyncpg_type_conversion(con: asyncpg.Connection):
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
