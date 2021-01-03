from asyncpg.exceptions import UniqueViolationError

from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


@db_test(clean_db=True)
async def create_pw_basic(t: TestEnv):
    email = "test@TEST.com"
    pw_hash = "test-hash"
    user_id = await sql.call_fn(t, "ac_user_create_pw", [
        ("p_email", email, "TEXT"),
        ("p_pw_hash", pw_hash, "TEXT"),
        ("p_timezone", t.timezone, "TEXT")
    ])
    user_q = """
    SELECT user_id,
           email_lower,
           created,
           updated,
           pw_hash
      FROM ac_user
     WHERE user_id = $1
    """
    record = (await sql.ad_hoc(t, user_q, [user_id]))[0]
    assert record["email_lower"] == email.lower()
    assert record["created"] is not None
    assert record["created"] == record["updated"]
    assert record["pw_hash"] == pw_hash
    return


@db_test(clean_db=True)
async def unique_emails(t: TestEnv):
    email = "the@test-email.com"
    pw_hash = "hihihi"
    await sql.call_fn(t, "ac_user_create_pw", [
        ("p_email", email, "TEXT"),
        ("p_pw_hash", pw_hash, "TEXT"),
        ("p_timezone", t.timezone, "TEXT"),
    ])
    try:
        await sql.call_fn(t, "ac_user_create_pw", [
            ("p_email", email, "TEXT"),
            ("p_pw_hash", pw_hash, "TEXT"),
            ("p_timezone", t.timezone, "TEXT"),
        ])
    except UniqueViolationError:
        return
    raise Exception("created two users with the same email")


@db_test(clean_db=True)
async def invalid_emails(t: TestEnv):
    pw_hash = "xxx"

    async def ensure_invalid(email: str):
        try:
            await sql.call_fn(t, "ac_user_create_pw", [
                ("p_email", email, "TEXT"),
                ("p_pw_hash", pw_hash, "TEXT"),
            ])
        except Exception:
            return
        raise Exception("invalid email inserted - {}".format(email))
    await ensure_invalid("email")
    await ensure_invalid("no@@")
    await ensure_invalid("no@@thing.com")
    await ensure_invalid("no@thing")
    await ensure_invalid("@thing.com")
    return


@db_test(clean_db=True)
async def create_provider_basic(t: TestEnv):
    email = "a-TEST@thing.com"
    provider_type = "GOOGLE"
    provider_token = "----test-token---"
    user_id = await sql.call_fn(t, "ac_user_create_provider", [
        ("p_email", email, "TEXT"),
        ("p_provider_type", provider_type, "PROVIDER_T"),
        ("p_provider_token", provider_token, "TEXT"),
        ("p_timezone", t.timezone, "TEXT"),
    ])
    query_s = """
    SELECT user_id,
           email_lower,
           created,
           updated,
           pw_hash
      FROM ac_user
     WHERE user_id = $1
    """
    query_res = (await sql.ad_hoc(t, query_s, [user_id]))[0]
    assert query_res["email_lower"] == email.lower()
    assert query_res["created"] is not None
    assert query_res["created"] == query_res["updated"]
    assert query_res["pw_hash"] is None
    return
