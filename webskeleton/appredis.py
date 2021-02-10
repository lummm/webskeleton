from typing import Optional

import aioredis  # type: ignore

from webskeleton.env import ENV


pool: aioredis.pool.ConnectionsPool


def _check_pool():
    if not pool:
        raise Exception("redis not connected")
    return


async def connect():
    global pool
    pool = await aioredis.create_redis_pool(f"redis://{ENV.REDIS_HOST}")
    return


async def set_str(key: str, value: str, expire_s: int = 0) -> None:
    _check_pool()
    await pool.set(key, value, expire=expire_s)
    return


async def get_str(key: str) -> Optional[str]:
    _check_pool()
    res = await pool.get(key)
    if not res:
        return None
    return res.decode("utf-8")
