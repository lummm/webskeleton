import json
import logging
from typing import Optional

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


LICENSE_CODE = "test-license"
LICENSE_ID = ""


async def create_license(t: TestEnv):
    license_id = await sql.call_fn(t, "license_create", [
        ("p_license_code", LICENSE_CODE, "TEXT"),
        ("p_adhoc", "{}", "JSON"),
    ])
    global LICENSE_ID
    LICENSE_ID = license_id
    return


async def grant_license(t: TestEnv, quantity: Optional[int]):
    await sql.call_fn(t, "user_license_set_granted", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_license_id", LICENSE_ID, "UUID"),
        ("p_quantity", quantity, "INTEGER"),
    ])
    return


async def attempt_grant_one(t: TestEnv):
    granted = await sql.call_fn(t, "sys.user_consume_license", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_license_code", LICENSE_CODE, "TEXT"),
        ("p_quantity", 1, "INTEGER"),
    ])
    return granted


async def get_license_granted(t: TestEnv):
    res = await sql.call_fn(t, "sys.user_license_granted", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_license_code", LICENSE_CODE, "TEXT"),
    ])
    return res


@db_test(clean_db=True)
async def licenses(t: TestEnv):
    await create_license(t)
    await grant_license(t, 2)
    granted = await get_license_granted(t)
    assert not granted["infinite"]
    assert granted["available"] == 2
    assert await attempt_grant_one(t)
    granted = await get_license_granted(t)
    assert granted["available"] == 1
    assert await attempt_grant_one(t)
    granted = await get_license_granted(t)
    assert granted["available"] == 0
    await grant_license(t, 1)
    granted = await get_license_granted(t)
    assert granted["available"] == 1
    assert await attempt_grant_one(t)
    granted = await get_license_granted(t)
    assert granted["available"] == 0
    await grant_license(t, None)
    granted = await get_license_granted(t)
    for i in range(10):
        assert await attempt_grant_one(t)
    return


@db_test(clean_db=True)
async def provision_license(t: TestEnv):
    await create_license(t)
    await sql.call_fn(t, "sys.user_provision_license", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_license_code", LICENSE_CODE, "TEXT"),
    ])
    granted = await get_license_granted(t)
    assert not granted["infinite"]
    assert granted["available"] == 1
    return
