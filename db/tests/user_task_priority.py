from typing import List
import uuid

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


TASK_TYPE = "INDIVIDUAL"
TASK_IDS: List


async def init_group(t: TestEnv) -> str:
    group_id = await sql.call_fn(t, "work_group_create", [
        ("p_owner_id", fmk.TEST_USER_ID, "UUID"),
        ("p_title", "TEST GROUP", "TEXT"),
    ])
    assert group_id
    return group_id


async def init_user_tasks(t: TestEnv):
    group_id = await init_group(t)
    task_ids = []
    for i in range(10):
        task_id = await sql.call_fn(t, "user_task_create", [
            ("p_user_id", fmk.TEST_USER_ID, "UUID"),
            ("p_group_id", group_id, "UUID"),
            ("p_task_type", TASK_TYPE, "USER_TASK_T"),
            ("p_title", "Task title {}".format(i), "TEXT"),
        ])
        task_ids.append(task_id)
    global TASK_IDS
    TASK_IDS = task_ids
    return


@db_test(clean_db=True)
async def update_priority(t: TestEnv):
    await init_user_tasks(t)
    new_task_ids = TASK_IDS
    new_task_ids.reverse()
    updated = await sql.call_fn(t, "user_task_priority_update", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_task_type", TASK_TYPE, "USER_TASK_T"),
        ("p_priority_l", new_task_ids, "UUID[]"),
    ])
    assert updated == 1
    query_s = """
    SELECT priority_l
      FROM user_task_priority
     WHERE user_id = $1
       AND task_type = $2
    """
    res = (await sql.ad_hoc(t, query_s, [fmk.TEST_USER_ID, TASK_TYPE]))[0]
    assert res["priority_l"] == new_task_ids
    return


@db_test(clean_db=True)
async def delete_task(t: TestEnv):
    await init_user_tasks(t)
    deleted = await sql.call_fn(t, "user_task_delete", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_task_id", TASK_IDS[0], "UUID"),
    ])
    assert deleted == 1
    query_s = """
    SELECT priority_l
      FROM user_task_priority
     WHERE user_id = $1
       AND task_type = $2
    """
    res = (await sql.ad_hoc(t, query_s, [fmk.TEST_USER_ID, TASK_TYPE]))[0]
    assert TASK_IDS[0] not in res["priority_l"]
    return


@db_test(clean_db=True)
async def no_such_task(t: TestEnv):
    await init_user_tasks(t)
    try:
        await sql.call_fn(t, "user_task_priority_create", [
            ("p_user_id", fmk.TEST_USER_ID, "UUID"),
            ("p_task_type", TASK_TYPE, "USER_TASK_T"),
            ("p_priority_l", [str(uuid.uuid4())], "UUID[]"),
        ])
    except Exception:
        return
    raise Exception("added priority for non-existent task")


@db_test(clean_db=True)
async def no_such_user(t: TestEnv):
    try:
        await sql.call_fn(t, "user_task_priority_create", [
            ("p_user_id", str(uuid.uuid4()), "UUID"),
            ("p_task_type", TASK_TYPE, "USER_TASK_T"),
            ("p_priority_l", [], "UUID[]"),
        ])
    except Exception:
        return
    raise Exception("added priority for non-existent user")
