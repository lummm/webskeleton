from datetime import datetime
import logging
import time

import pytz

import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


@db_test(clean_db=True)
async def user_notification_daily_load(t: TestEnv):
    LOAD_WINDOW_S = 300
    NOTIFICATION_TYPE = "DAY_START"
    init_res = await sql.call_fn(t, "sys.new_user_setup", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
    ])
    assert init_res
    workday_update = await sql.call_fn(t, "sys.user_set_workdays", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_workdays", [0, 1, 2, 3, 4, 5, 6], "INTEGER[]"),  # every day bruh
    ])
    assert workday_update["updated"] == 1
    target_dt = datetime.fromtimestamp(time.time() + (LOAD_WINDOW_S // 2),
                                       pytz.timezone(t.timezone))
    notification = await sql.call_fn(t, "sys.user_notification_set", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_notification_type", NOTIFICATION_TYPE, "NOTIFICATION_T"),
        ("p_sched_time_h", target_dt.hour, "INTEGER"),
        ("p_sched_time_m", target_dt.minute, "INTEGER"),
    ])
    load_res = await sql.call_fn(t, "sys.user_notification_daily_load", [
        ("p_max_future_ts", time.time() + LOAD_WINDOW_S, "INTEGER"),
    ])
    assert load_res
    matches = [r for r in load_res
               if r["notification_id"] == notification["notification_id"]]
    assert matches
    match = matches[0]
    assert match["user_id"] == fmk.TEST_USER_ID
    assert match["notification_type"] == NOTIFICATION_TYPE
    target_minute = target_dt.replace(second=0, microsecond=0)
    assert match["sched_time"] == target_minute.timestamp()
    return
