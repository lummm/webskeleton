from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


async def init_user(t: TestEnv, email: str) -> str:
    user_id = await sql.call_fn(t, "ac_user_create_pw", [
        ("p_email", email, "TEXT"),
        ("p_pw_hash", "hihihi", "TEXT"),
        ("p_timezone", t.timezone, "TEXT")
    ])
    return user_id


@db_test(clean_db=True)
async def work_group_new(t: TestEnv):
    user_id = await init_user(t, "test@test.com")
    create_res = await sql.call_fn(t, "sys.work_group_new", [
        ("p_user_id", user_id, "UUID"),
        ("p_title", "Test Group", "TEXT"),
        ("p_adhoc", "{}", "JSON"),
    ])
    assert create_res["created"] == 1
    assert create_res["users_added"] == 1
    assert create_res["group_id"]
    return
