from typing import List


from . import db


async def user_owns_all(user_id: str, obj_ids: List[str]) -> bool:
    res = await db.fetch_val(
        """
    SELECT count(uo.obj_id) = array_length($2, 1)
      FROM user_ownership uo
      JOIN unnest($2::uuid[]) objects
        ON objects = uo.obj_id
     WHERE user_id = $1
    """,
        [user_id, obj_ids],
    )
    return res == 1
