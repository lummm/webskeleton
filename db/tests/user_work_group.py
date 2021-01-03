from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


email = "test@test.com"
title = "Test Title"


async def init_user(t: TestEnv, email: str) -> str:
    user_id = await sql.call_fn(t, "ac_user_create_pw", [
        ("p_email", email, "TEXT"),
        ("p_pw_hash", "hihihi", "TEXT"),
        ("p_timezone", t.timezone, "TEXT")
    ])
    assert user_id
    return user_id


async def init_group(t: TestEnv, user_id: str) -> str:
    group_id = await sql.call_fn(t, "work_group_create", [
        ("p_owner_id", user_id, "UUID"),
        ("p_title", title, "TEXT"),
    ])
    assert group_id
    return group_id


@db_test(clean_db=True)
async def user_work_group_create(t: TestEnv):
    user_id = await init_user(t, email)
    group_id = await init_group(t, user_id)
    res = await sql.call_fn(t, "user_work_group_create", [
        ("p_user_id", user_id, "UUID"),
        ("p_group_id", group_id, "UUID"),
    ])
    assert res == 1
    assert (await sql.ad_hoc(t, """
    SELECT 1 AS exists
      FROM user_work_group
     WHERE user_id = $1
       AND group_id = $2
    """, [user_id, group_id]))[0]["exists"]
    return user_id, group_id


@db_test(clean_db=True)
async def user_work_group_delete(t: TestEnv):
    user_id, group_id = await user_work_group_create(t)
    res = await sql.call_fn(t, "user_work_group_delete", [
        ("p_user_id", user_id, "UUID"),
        ("p_group_id", group_id, "UUID"),
    ])
    assert res == 1
    assert not (await sql.ad_hoc(t, """
    SELECT 1 AS exists
      FROM user_work_group
     WHERE user_id = $1
       AND group_id = $2
    """, [user_id, group_id]))
    return
