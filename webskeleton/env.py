"""
Environment variables
"""

import os
from typing import NamedTuple


class _ENV(NamedTuple):
    # -- required
    PGPASSWORD: str = os.environ["PGPASSWORD"]
    # this signs jwts
    KEY: str = os.environ["KEY"]
    PORT: int = int(os.environ["PORT"])

    # -- optional
    PGHOST: str = os.environ.get("PGHOST", "localhost")
    PGUSER: str = os.environ.get("PGUSER", "postgres")
    PGDB: str = os.environ.get("PGDB", "postgres")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    # size in bytes
    REFRESH_TOKEN_SIZE: int = int(os.environ.get("REFRESH_TOKEN_SIZE", 24))
    ACCESS_TOKEN_EXP_S: int = int(os.environ.get("ACCESS_TOKEN_EXP_S", 1800))  # 30 mins
    REFRESH_TOKEN_EXP_S: int = int(
        os.environ.get("REFRESH_TOKEN_EXP_S", 259200)
    )  # 3 days


ENV = _ENV()
