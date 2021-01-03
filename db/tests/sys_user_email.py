import db_test_fw as fmk
from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


thread_id = "z1x2c3v4b5"
MSG_TYPE = "NOTIFICATION"


@db_test(clean_db=True)
async def user_email_thread_start(t: TestEnv):
    thread_res = await sql.call_fn(t, "sys.user_email_thread_start", [
        ("p_user_id", fmk.TEST_USER_ID, "UUID"),
        ("p_msg_type", MSG_TYPE, "USER_MSG_T"),
        ("p_email_thread_id", thread_id, "TEXT"),
        ("p_adhoc", "{}", "JSON"),
    ])
    assert thread_res["log_id"]
    return
