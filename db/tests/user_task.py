import logging
from typing import Dict
import uuid

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


TASK_TYPE = "INDIVIDUAL"
TASK_TITLE = "Test Task Title"
TASK_ID = None


async def get_details(t: TestEnv) -> Dict:
    return (await sql.ad_hoc(t, """
    SELECT title,
           completed,
           description
      FROM user_task_details
     WHERE task_id = $1
    """, [TASK_ID]))[0]


async def init_group(t: TestEnv) -> str:
    group_id = await sql.call_fn(t, "work_group_create", [
        ("p_owner_id", fmk.TEST_USER_ID, "UUID"),
        ("p_title", "TEST GROUP", "TEXT"),
    ])
    assert group_id
    return group_id


@db_test(clean_db=True)
async def create_basic(t: TestEnv):
    group_id = await init_group(t)
    task_id = await sql.call_fn(t, "user_task_create", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_group_id", group_id, "UUID"),
        ("p_task_type", TASK_TYPE, "USER_TASK_T"),
        ("p_title", TASK_TITLE, "TEXT")
    ])
    global TASK_ID
    TASK_ID = task_id
    query_res = (await sql.ad_hoc(t, """
    SELECT created,
           user_id,
           task_type
      FROM user_task
     WHERE task_id = $1
    """, [task_id]))[0]
    assert str(query_res["user_id"]) == fmk.TEST_USER_ID
    assert query_res["created"] is not None
    assert query_res["task_type"] == TASK_TYPE
    details = await get_details(t)
    assert details["title"] == TASK_TITLE
    return


@db_test(clean_db=True)
async def update_task(t: TestEnv):
    await create_basic(t)
    new_title = "NEW TITLE"
    await sql.call_fn(t, "user_task_update", [
        ("p_task_id", TASK_ID, "UUID"),
        ("p_title", new_title, "TEXT"),
    ])
    details = await get_details(t)
    assert details["title"] == new_title
    await sql.call_fn(t, "user_task_update", [
        ("p_task_id", TASK_ID, "UUID"),
        ("p_completed", True, "BOOLEAN"),
    ])
    details = await get_details(t)
    assert details["completed"]
    return


@db_test(clean_db=True)
async def no_such_user(t: TestEnv):
    group_id = await init_group(t)
    try:
        await sql.call_fn(t, "user_task_create", [
            ("p_user_id", str(uuid.uuid4()), "UUID"),
            ("p_group_id", group_id, "UUID"),
            ("p_task_type", TASK_TYPE, "USER_TASK_T"),
        ])
    except Exception:
        return
    raise Exception("created task for non-existent user")


@db_test(clean_db=True)
async def delete_task(t: TestEnv):
    await create_basic(t)
    deleted = await sql.call_fn(t, "user_task_delete", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_task_id", TASK_ID, "UUID"),
    ])
    assert deleted == 1
    query_s = """
    SELECT task_id
      FROM user_task
     WHERE task_id = $1
    """
    query_res = (await sql.ad_hoc(t, query_s, [TASK_ID]))
    assert not query_res
    return
