import asyncio
import json
import logging
import pprint
from typing import List
from types import SimpleNamespace

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


class State(SimpleNamespace):
    foreign_user_id: str
    foreign_group_ids: List[str]
    group_ids: List[str]
    # task_ids: List[str]
    # foreign_task_ids: List[str]


state = State()

N_GROUPS = 4


async def create_foreign_user(t: TestEnv):
    state.foreign_user_id = await sql.call_fn(t, "ac_user_create_pw", [
        ("p_email", "fake@email.com", "TEXT"),
        ("p_pw_hash", "a1s2d3f4g5-hash", "TEXT"),
        ("p_timezone", "America/Vancouver", "TEXT"),
    ])
    return


async def setup(t: TestEnv, n: int):
    async def _create_groups(user_id: str):
        res = [await sql.call_fn(t, "sys.work_group_new", [
            ("p_user_id", user_id, "UUID"),
            ("p_title", f"Group {i}", "TEXT"),
            ("p_adhoc", json.dumps({}), "JSON"),
        ]) for i in range(n)]
        return [r["group_id"] for r in res]
    await sql.ad_hoc(t, """
    DELETE FROM work_group
          WHERE owner_id = $1
      RETURNING 1
    """, [fmk.TEST_USER_ID])
    await create_foreign_user(t)
    state.group_ids = await _create_groups(fmk.TEST_USER_ID)
    state.foreign_group_ids = await _create_groups(state.foreign_user_id)
    return


async def foreign_user_join_groups(t: TestEnv, n: int):
    [await sql.call_fn(t, "sys.user_work_group_join", [
        ("p_user_id", state.foreign_user_id, "UUID"),
        ("p_group_id", state.group_ids[i], "UUID"),
    ]) for i in range(n)]
    return


async def create_tasks(
        t: TestEnv,
        group_id: str,
        user_id: str,
        n: int
) -> List[str]:
    res = [await sql.call_fn(t, "sys.user_task_create", [
        ("p_user_id", user_id, "UUID"),
        ("p_group_id", group_id, "UUID"),
        ("p_title", f"{user_id} Task {i}", "TEXT"),
        ("p_task_type", "INDIVIDUAL", "USER_TASK_T"),
        ("p_description", "None", "TEXT"),
    ]) for i in range(n)]
    return [r["task_id"] for r in res]


@db_test(clean_db=True)
async def my_groups(t: TestEnv):
    await setup(t, N_GROUPS)
    query_res = await sql.ad_hoc(t, """
    SELECT group_id
      FROM api.my_groups
    """, [])
    assert len(query_res) == N_GROUPS
    assert set(r["group_id"] for r in query_res) == set(state.group_ids)
    return


@db_test(clean_db=True)
async def my_group_users(t: TestEnv):
    await setup(t, N_GROUPS)
    n_joined = N_GROUPS - 2
    await foreign_user_join_groups(t, n_joined)
    query_res = await sql.ad_hoc(t, """
    SELECT group_id,
           user_id
      FROM api.my_group_users
    """, [])
    groups_with_user = zip([fmk.TEST_USER_ID] * N_GROUPS, state.group_ids)
    groups_with_foreign = zip([state.foreign_user_id] * n_joined,
                              state.group_ids)
    exp_rows = list(groups_with_user) + list(groups_with_foreign)
    assert len(query_res) == len(exp_rows)
    query_rows = [(r["user_id"], r["group_id"]) for r in query_res]
    assert set(query_rows) == set(exp_rows)
    return


@db_test(clean_db=True)
async def my_group_tasks(t: TestEnv):
    await setup(t, N_GROUPS)
    n_joined = N_GROUPS - 2
    await foreign_user_join_groups(t, n_joined)
    my_task_ids = await create_tasks(
        t, state.group_ids[0], fmk.TEST_USER_ID, 3)
    foreign_shared_task_ids = await create_tasks(
        t, state.group_ids[0], state.foreign_user_id, 3)
    foreign_task_ids = await create_tasks(
        t, state.foreign_group_ids[0], state.foreign_user_id, 3)
    query_res = await sql.ad_hoc(t, """
    SELECT group_id,
           user_id,
           task_id
      FROM api.my_group_tasks
    """, [])
    user_rows = [(state.group_ids[0], fmk.TEST_USER_ID, task_id)
                 for task_id in my_task_ids]
    foreign_shared_rows = [(state.group_ids[0], state.foreign_user_id, task_id)
                           for task_id in foreign_shared_task_ids]
    # foreign_rows = [
    #     (state.foreign_group_ids[0], state.foreign_user_id, task_id)
    #     for task_id in foreign_task_ids]

    exp_rows = user_rows + foreign_shared_rows
    query_rows = [(r["group_id"], r["user_id"], r["task_id"])
                  for r in query_res]

    def dump():
        logging.info("shared group: %s", state.group_ids[0])
        logging.info("foreign group: %s", state.foreign_group_ids[0])
        logging.info("my task ids: %s", my_task_ids)
        logging.info("foreign shared task ids: %s", foreign_shared_task_ids)
        logging.info("foreign task ids: %s", foreign_task_ids)
        logging.info("my user id %s", fmk.TEST_USER_ID)
        logging.info("foreign user id %s", state.foreign_user_id)
        raise Exception("group task mismatch")
    for r in exp_rows:
        if r not in query_rows:
            logging.error("expected row %s not found", r)
            dump()
    for r in query_rows:
        if r not in exp_rows:
            logging.error("found row %s when not expected", r)
            dump()
    return
