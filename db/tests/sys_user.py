import json
import logging

from db_test_fw import db_test
from db_test_fw import TestEnv
import sql


email = "test-email@email.com"
email_2 = "test-2-email@email.com"
pw_hash = "hihihihi12345"
given_name = "Great"
family_name = "User"


async def create_user(t: TestEnv):
    user_res = await sql.call_fn(t, "sys.new_user_pw", [
        ("p_email", email, "TEXT"),
        ("p_pw_hash", pw_hash, "TEXT"),
        ("p_timezone", t.timezone, "TEXT"),
        ("p_adhoc", json.dumps({
            "given_name": given_name,
            "family_name": family_name,
        }), "JSONB"),
    ])
    return user_res


@db_test(clean_db=True)
async def get_user_exists(t: TestEnv):
    exists_res = await sql.call_fn(t, "sys.get_user_exists", [
        ("p_email", email, "TEXT"),
    ])
    assert not exists_res
    user_res = await create_user(t)
    assert user_res["created"] == 1
    exists = await sql.call_fn(t, "sys.get_user_exists", [
        ("p_email", email, "TEXT"),
    ])
    assert exists
    return


@db_test(clean_db=True)
async def get_user_slim(t: TestEnv):
    await create_user(t)
    user_res = await sql.call_fn(t, "sys.get_user_slim", [
        ("p_email", email, "TEXT"),
    ])
    assert user_res
    assert user_res["user_id"]
    assert user_res["pw_hash"] == pw_hash
    assert user_res["timezone"] == t.timezone
    assert not user_res["verified"]
    provider_res = await sql.call_fn(t, "sys.new_user_provider", [
        ("p_email", email_2, "TEXT"),
        ("p_provider_type", "GOOGLE", "PROVIDER_T"),
        ("p_provider_token", "garbage-token123", "TEXT"),
        ("p_timezone", t.timezone, "TEXT"),
    ])
    assert provider_res["created"] == 1
    provider_user_res = await sql.call_fn(t, "sys.get_user_slim", [
        ("p_email", email_2, "TEXT"),
    ])
    assert provider_user_res["verified"]
    return


@db_test(clean_db=True)
async def new_user_pw(t: TestEnv):
    user_res = await create_user(t)
    assert user_res["created"] == 1
    record = (await sql.ad_hoc(t, """
    SELECT adhoc
      FROM ac_user
     WHERE user_id = $1
    """, [user_res["user_id"]]))[0]
    assert not record["adhoc"]["verified"]  # not verified by default
    user_res = await create_user(t)
    assert user_res["created"] == 0
    return


@db_test(clean_db=True)
async def new_google_user_provider(t: TestEnv):
    user_res = await sql.call_fn(t, "sys.new_user_provider", [
        ("p_email", email, "TEXT"),
        ("p_provider_type", "GOOGLE", "PROVIDER_T"),
        ("p_provider_token", "gibberish-token", "TEXT"),
        ("p_timezone", t.timezone, "TEXT"),
    ])
    assert user_res["created"] == 1
    assert user_res["user_id"]
    record = (await sql.ad_hoc(t, """
    SELECT adhoc
      FROM ac_user
     WHERE user_id = $1
    """, [user_res["user_id"]]))[0]
    assert record["adhoc"]["verified"]  # provider is auto-verified
    return


@db_test(clean_db=True)
async def user_set_workdays(t: TestEnv):
    workdays = [0, 1, 2, 3, 4, 5, 6]
    user_res = await create_user(t)
    assert user_res["created"] == 1
    assert user_res["user_id"]
    update_res = await sql.call_fn(t, "sys.user_set_workdays", [
        ("p_user_id", user_res["user_id"], "UUID"),
        ("p_workdays", workdays, "INTEGER[]"),
    ])
    assert update_res["updated"] == 1
    return


@db_test(clean_db=True)
async def user_adhoc(t: TestEnv):
    user_res = await create_user(t)
    user_id = user_res["user_id"]
    update_1 = {"nested": {"object": True}}
    res = await sql.call_fn(t, "sys.user_update_adhoc", [
        ("p_user_id", user_id, "UUID"),
        ("p_adhoc", json.dumps(update_1), "JSON"),
    ])
    assert res and res["updated"] == 1
    adhoc_data = await sql.call_fn(t, "sys.user_get_adhoc", [
        ("p_user_id", user_id, "UUID"),
    ])
    assert adhoc_data["nested"]["object"]
    update_2 = {"nested": {"another": True,
                           "object": False},
                "thing": False}
    res = await sql.call_fn(t, "sys.user_update_adhoc", [
        ("p_user_id", user_id, "UUID"),
        ("p_adhoc", json.dumps(update_2), "JSON"),
    ])
    assert res and res["updated"] == 1
    adhoc_data = await sql.call_fn(t, "sys.user_get_adhoc", [
        ("p_user_id", user_id, "UUID"),
    ])
    assert not adhoc_data["nested"]["object"]
    assert adhoc_data["nested"]["another"]
    assert not adhoc_data["thing"]
    return
