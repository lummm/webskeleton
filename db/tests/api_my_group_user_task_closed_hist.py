from datetime import datetime
import logging
import pprint

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


HIST_RECORDS = 5


async def create_task_history(t: TestEnv, offset: int) -> str:
    task_id = await sql.call_fn(t, "user_task_create", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_group_id", fmk.TEST_GROUP_ID, "UUID"),
        ("p_task_type", "INDIVIDUAL", "USER_TASK_T"),
        ("p_title", "Test task", "TEXT"),
    ])
    for i in range(1, HIST_RECORDS + 1):
        details_id = await sql.call_fn(t, "task_details_hist_create", [
            ("p_task_id", task_id, "UUID"),
            ("p_title", "Test task", "TEXT"),
            ("p_completed", ((i + offset) % 2) == 0, "BOOLEAN"),
        ])
        await sql.ad_hoc(t, """
        UPDATE task_details_hist
           SET created = now() - (INTERVAL '1' DAY) * $2
         WHERE task_details_id = $1
     RETURNING 1
        """, [details_id, i])
    return task_id


@db_test(clean_db=True)
async def test_historical_counts(t: TestEnv) -> None:
    task_0 = await create_task_history(t, 0)
    task_1 = await create_task_history(t, 1)
    timestamps = await sql.ad_hoc(t, """
    WITH timestamps AS (
      SELECT now() - (INTERVAL '1' DAY) * i ts
        FROM generate_series(1, $1) i
    )
    SELECT array_agg(extract(epoch FROM ts.ts))
      FROM timestamps ts
    """, [HIST_RECORDS])
    timestamps = sorted(timestamps[0]["array_agg"])
    res = await sql.call_fn(t, "api.my_group_user_task_closed_hist", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_group_id", fmk.TEST_GROUP_ID, "UUID"),
        ("p_timestamps", timestamps, "NUMERIC[]"),
    ])
    for i in range(len(timestamps)):
        ts = timestamps[i]
        task_0_res = [row for row in res
                      if row["task_id"] == task_0
                      and row["target_ts"] == ts][0]
        assert task_0_res["completed"] == (((i + 1) % 2) == 0)
        task_1_res = [row for row in res
                      if row["task_id"] == task_1
                      and row["target_ts"] == ts][0]
        assert task_1_res["completed"] == (((i) % 2) == 0)
    return
