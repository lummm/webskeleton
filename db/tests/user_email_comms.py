import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


MSG_TYPES = [
    "NOTIFICATION",
]


@db_test(clean_db=True)
async def user_email_comms_create(t: TestEnv):
    for msg_type in MSG_TYPES:
        res = await sql.call_fn(t, "user_email_comms_create", [
            ("p_user_id", fmk.TEST_USER_ID, "UUID"),
            ("p_email_thread_id", "test-thread1", "TEXT"),
            ("p_msg_type", msg_type, "USER_MSG_T"),
        ])
        assert res
    return
