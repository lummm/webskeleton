import logging
import json

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


async def create_group(t: TestEnv) -> str:
    group_id = await sql.call_fn(t, "work_group_create", [
        ("p_owner_id", fmk.TEST_USER_ID, "UUID"),
        ("p_title", "TEST GROUP", "TEXT"),
    ])
    assert group_id
    return group_id


async def create_task(
        t: TestEnv,
        user_id: str,
        title: str,
        desc: str
) -> str:
    group_id = await create_group(t)
    task_type = "INDIVIDUAL"
    create_res = await sql.call_fn(t, "sys.user_task_create", [
        ("p_user_id", user_id, "UUID"),
        ("p_group_id", group_id, "UUID"),
        ("p_title", title, "TEXT"),
        ("p_task_type", task_type, "USER_TASK_T"),
        ("p_description", desc, "TEXT"),
    ])
    assert create_res["created"] == 1
    return create_res["task_id"]


@db_test(clean_db=True)
async def user_task_create(t: TestEnv) -> None:
    task_title = "A big test task title"
    task_desc = "Big ole description"
    task_id = await create_task(t, fmk.TEST_USER_ID, task_title, task_desc)
    assert task_id
    return


@db_test(clean_db=True)
async def user_task_update(t: TestEnv) -> None:
    task_title = "A big test task title"
    task_desc = "Big ole description"
    task_id = await create_task(t, fmk.TEST_USER_ID, task_title, task_desc)
    assert task_id
    await sql.call_fn(t, "sys.user_task_update", [
        ("p_task_id", task_id, "UUID"),
        ("p_update", json.dumps({"completed": True}), "JSON"),
    ])

    async def get_record():
        rows = await sql.call_fn(t, "sys.get_user_task_details", [
            ("p_user_id", fmk.TEST_USER_ID, "UUID"),
            ("p_restrict_task_ids", [task_id], "UUID[]"),
        ])
        return rows[0]
    rec = await get_record()
    assert rec["completed"]
    assert rec["title"] == task_title
    assert rec["description"] == task_desc
    return


@db_test(clean_db=True)
async def user_task_details(t: TestEnv) -> None:
    tasks = [{
        "title": "Task title 1",
        "desc": "Description 1",
    }, {
        "title": "Task title 2",
        "desc": "Description 2",
    }]
    for task in tasks:
        task["task_id"] = await create_task(
            t, fmk.TEST_USER_ID, task["title"], task["desc"])
    res = await sql.call_fn(t, "sys.get_user_task_details", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_restrict_task_ids", None, "UUID[]"),
    ])
    assert [t["task_id"] for t in res] == [t["task_id"] for t in tasks]
    res = await sql.call_fn(t, "sys.get_user_task_details", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_restrict_task_ids", [tasks[0]["task_id"]], "UUID[]"),
    ])
    assert [t["task_id"] for t in res] == [tasks[0]["task_id"]]
    res = await sql.call_fn(t, "sys.get_user_task_details", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_restrict_task_ids", [t["task_id"] for t in tasks], "UUID[]"),
    ])
    assert [t["task_id"] for t in res] == [t["task_id"] for t in tasks]
    return
