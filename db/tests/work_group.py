from typing import Tuple

from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


user_1 = "test@test.com"
user_2 = "test-2@test.com"


async def init_user(t: TestEnv, email: str) -> str:
    user_id = await sql.call_fn(t, "ac_user_create_pw", [
        ("p_email", email, "TEXT"),
        ("p_pw_hash", "hihihi", "TEXT"),
        ("p_timezone", t.timezone, "TEXT")
    ])
    return user_id


@db_test(clean_db=True)
async def work_group_create(t: TestEnv) -> Tuple[str, str]:
    user_id = await init_user(t, user_1)
    title = "Test Group Title"
    group_id = await sql.call_fn(t, "work_group_create", [
        ("p_owner_id", user_id, "UUID"),
        ("p_title", title, "TEXT"),
    ])
    assert group_id
    res = await sql.ad_hoc(t, """
    SELECT owner_id,
           title
      FROM work_group
     WHERE group_id = $1
    """, [group_id])
    assert res[0]["owner_id"] == user_id
    assert res[0]["title"] == title
    return user_id, group_id


@db_test(clean_db=True)
async def work_group_update(t: TestEnv):
    user_id, group_id = await work_group_create(t)
    new_user_id = await init_user(t, user_2)
    update_res = await sql.call_fn(t, "work_group_update", [
        ("p_group_id", group_id, "UUID"),
        ("p_owner_id", new_user_id, "UUID"),
    ])
    assert update_res == 1
    new_title = "A New Title"
    update_res = await sql.call_fn(t, "work_group_update", [
        ("p_group_id", group_id, "UUID"),
        ("p_title", new_title, "TEXT"),
    ])
    assert update_res == 1
    rec = (await sql.ad_hoc(t, """
    SELECT owner_id,
           title
      FROM work_group
     WHERE group_id = $1
    """, [group_id]))[0]
    assert rec["owner_id"] == new_user_id
    assert rec["title"] == new_title
    return
