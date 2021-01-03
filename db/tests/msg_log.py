from datetime import datetime
import json
import logging
import time

import pytz

from db_test_fw import db_test
from db_test_fw import TestEnv
import db_test_fw as fmk
import sql


LOAD_RES_S = 200


async def set_notification(t: TestEnv):
    sched_ts = time.time() + 62
    sched_dt = datetime.fromtimestamp(sched_ts, pytz.timezone(t.timezone))
    await sql.ad_hoc(t, """DELETE FROM user_notification RETURNING 1""", [])
    await sql.call_fn(t, "sys.user_notification_set", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_notification_type", "DAY_START", "NOTIFICATION_T"),
        ("p_sched_time_h", sched_dt.hour, "INTEGER"),
        ("p_sched_time_m", sched_dt.minute, "INTEGER"),
    ])
    msg_q_res = await sql.ad_hoc(t, """
    SELECT notification_id,
           sched_time,
           url,
           body
      FROM notification_msg
    """, [])
    assert msg_q_res and len(msg_q_res) == 1
    msg = msg_q_res[0]
    expected_sched_ts = int(sched_dt
                            .replace(second=0, microsecond=0)
                            .timestamp())
    assert msg["sched_time"] == expected_sched_ts
    assert msg["url"] == "/send/DAY_START"
    assert msg["body"]["user_id"] == fmk.TEST_USER_ID
    return msg


async def load_msg(t: TestEnv):
    msg_res = await sql.call_fn(t, "sys.load_msgs", [
        ("p_max_future_ts", time.time() + LOAD_RES_S, "NUMERIC")
    ])
    logging.info("loaded msgs %s", msg_res)
    assert msg_res
    return msg_res


@db_test(clean_db=True)
async def test_msging(t: TestEnv):
    await set_notification(t)
    await load_msg(t)
    return
