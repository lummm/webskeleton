from typing import NamedTuple, Dict

from box import Box
from pypika import Table


class AcUser(NamedTuple):
    user_id: str
    created: int
    updated: int
    email_lower: str
    pw_hash: str
    adhoc: Dict


ac_user_table = Table("ac_user")
ac_user = Box({
    'table_ref': ac_user_table,
    'user_id': ac_user_table.user_id,
    'created': ac_user_table.created,
    'updated': ac_user_table.updated,
    'email_lower': ac_user_table.email_lower,
    'pw_hash': ac_user_table.pw_hash,
    'adhoc': ac_user_table.adhoc,
})

