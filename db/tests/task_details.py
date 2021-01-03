import logging
from typing import Dict
from types import SimpleNamespace
import uuid

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


class State(SimpleNamespace):
    task_id: str
    details_hist_id: str


state = State()


async def create_group(t: TestEnv) -> str:
    group_id = await sql.call_fn(t, "work_group_create", [
        ("p_owner_id", fmk.TEST_USER_ID, "UUID"),
        ("p_title", "TEST GROUP", "TEXT"),
    ])
    assert group_id
    return group_id


async def create_task(t: TestEnv):
    group_id = await create_group(t)
    task_id = await sql.call_fn(t, "user_task_create", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_group_id", group_id, "UUID"),
        ("p_task_type", "INDIVIDUAL", "USER_TASK_T"),
        ("p_title", "Test title", "TEXT")
    ])
    assert task_id
    state.task_id = task_id
    return


@db_test(clean_db=True)
async def hist_create(t: TestEnv):
    await create_task(t)
    details_id = await sql.call_fn(t, "task_details_hist_create", [
        ("p_task_id", state.task_id, "UUID"),
        ("p_title", "New title", "TEXT"),
    ])
    assert details_id
    state.details_hist_id = details_id
    return


@db_test(clean_db=True)
async def hist_update(t: TestEnv):
    await hist_create(t)
    new_hist_id = await sql.call_fn(t, "task_details_hist_update", [
        ("p_task_details_id", state.details_hist_id, "UUID"),
        ("p_completed", True, "BOOLEAN"),
    ])
    assert new_hist_id
    rec = await sql.ad_hoc(t, """
    SELECT completed
      FROM task_details_hist
     WHERE task_details_id = $1
    """, [new_hist_id])
    assert rec
    assert rec[0]["completed"] == True
    return
