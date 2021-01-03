from typing import Dict

import webskeleton.db as db


async def ac_user_create_pw(p_email: str, p_pw_hash: str, p_adhoc: Dict = None) -> str:
    return await db.fetch_val("""
    SELECT sys.ac_user_create_pw(
      p_email => $1::text,
      p_pw_hash => $2::text,
      p_adhoc => $3::jsonb
    )
    """, (p_email, p_pw_hash, p_adhoc))


async def ac_user_update(p_user_id: str, p_adhoc: Dict = None) -> int:
    return await db.fetch_val("""
    SELECT sys.ac_user_update(
      p_user_id => $1::uuid,
      p_adhoc => $2::json
    )
    """, (p_user_id, p_adhoc))


async def user_license_set_granted(p_user_id: str, p_license_id: str, p_quantity: int) -> int:
    return await db.fetch_val("""
    SELECT sys.user_license_set_granted(
      p_user_id => $1::uuid,
      p_license_id => $2::uuid,
      p_quantity => $3::integer
    )
    """, (p_user_id, p_license_id, p_quantity))


async def ac_user_update(p_user_id: str, p_adhoc: Dict = None) -> int:
    return await db.fetch_val("""
    SELECT sys.ac_user_update(
      p_user_id => $1::uuid,
      p_adhoc => $2::jsonb
    )
    """, (p_user_id, p_adhoc))


async def tester(p_thing: str, p_thing_2: str, p_thing_3: str = 'hello') -> str:
    return await db.fetch_val("""
    SELECT sys.tester(
      p_thing => $1::text,
      p_thing_2 => $2::text,
      p_thing_3 => $3::text
    )
    """, (p_thing, p_thing_2, p_thing_3))


async def ac_permission_create(p_permission_name: str) -> str:
    return await db.fetch_val("""
    SELECT sys.ac_permission_create(
      p_permission_name => $1::text
    )
    """, (p_permission_name))


async def ac_role_permission_create(p_role_name: str, p_permission_name: str) -> int:
    return await db.fetch_val("""
    SELECT sys.ac_role_permission_create(
      p_role_name => $1::text,
      p_permission_name => $2::text
    )
    """, (p_role_name, p_permission_name))


async def ac_role_create(p_role_name: str) -> str:
    return await db.fetch_val("""
    SELECT sys.ac_role_create(
      p_role_name => $1::text
    )
    """, (p_role_name))


async def ac_user_delete(p_user_id: str) -> int:
    return await db.fetch_val("""
    SELECT sys.ac_user_delete(
      p_user_id => $1::uuid
    )
    """, (p_user_id))


async def ac_user_role_create(p_user_id: str, p_role_name: str) -> str:
    return await db.fetch_val("""
    SELECT sys.ac_user_role_create(
      p_user_id => $1::uuid,
      p_role_name => $2::text
    )
    """, (p_user_id, p_role_name))


async def license_create(p_license_code: str, p_adhoc: Dict = None) -> str:
    return await db.fetch_val("""
    SELECT sys.license_create(
      p_license_code => $1::text,
      p_adhoc => $2::jsonb
    )
    """, (p_license_code, p_adhoc))



