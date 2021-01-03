import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv

import sql


SCHED_TIME = (10, 15)
NOT_IDS = None


@db_test(clean_db=True)
async def create_all_types(t: TestEnv):
    await sql.ad_hoc(t, """
    DELETE FROM user_notification
          WHERE user_id = $1
      RETURNING notification_id
    """, [fmk.TEST_USER_ID])
    notification_types = ["DAY_START", "DAY_END"]
    not_ids = []
    for nt in notification_types:
        not_id = await sql.call_fn(t, "user_notification_create", [
            ("p_user_id", fmk.TEST_USER_ID, "UUID"),
            ("p_notification_type", nt, "NOTIFICATION_T"),
            ("p_sched_time_h", SCHED_TIME[0], "INTEGER"),
            ("p_sched_time_m", SCHED_TIME[1], "INTEGER"),
        ])
        not_ids.append(not_id)
    global NOT_IDS
    NOT_IDS = not_ids
    query_s = """
    SELECT sched_time_h,
           sched_time_m
      FROM user_notification
     WHERE notification_id = $1
    """
    for nid in not_ids:
        res = (await sql.ad_hoc(t, query_s, [nid]))[0]
        assert res["sched_time_h"] == SCHED_TIME[0]
        assert res["sched_time_m"] == SCHED_TIME[1]
    return


@db_test(clean_db=True)
async def update(t: TestEnv):
    await create_all_types(t)
    sched_time = (18, 21)
    updated = await sql.call_fn(t, "user_notification_update", [
        ("p_notification_id", NOT_IDS[0], "UUID"),
        ("p_sched_time_h", sched_time[0], "INTEGER"),
    ])
    assert updated == 1
    query_s = """
    SELECT sched_time_h,
           sched_time_m
      FROM user_notification
     WHERE notification_id = $1
    """
    res = (await sql.ad_hoc(t, query_s, [NOT_IDS[0]]))[0]
    assert res["sched_time_h"] == sched_time[0]
    assert res["sched_time_m"] == SCHED_TIME[1]
    updated = await sql.call_fn(t, "user_notification_update", [
        ("p_notification_id", NOT_IDS[0], "UUID"),
        ("p_sched_time_m", sched_time[1], "INTEGER"),
    ])
    assert updated == 1
    res = (await sql.ad_hoc(t, query_s, [NOT_IDS[0]]))[0]
    assert res["sched_time_h"] == sched_time[0]
    assert res["sched_time_m"] == sched_time[1]

    async def test_enabled_toggle(is_enabled: bool):
        query_s = """
        SELECT enabled
          FROM user_notification
         WHERE notification_id = $1
        """
        updated = await sql.call_fn(t, "user_notification_update", [
            ("p_notification_id", NOT_IDS[0], "UUID"),
            ("p_enabled", is_enabled, "BOOLEAN"),
        ])
        assert updated == 1
        res = (await sql.ad_hoc(t, query_s, [NOT_IDS[0]]))[0]
        assert res["enabled"] == is_enabled
    await test_enabled_toggle(False)
    await test_enabled_toggle(True)
    return
