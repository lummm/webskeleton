from webskeleton import db
from webskeleton import routedef

import shared.db_fns as db_fns


@routedef(method="GET", path="/big")
async def big_route(req):
    return {"hi": 3}


@routedef(method="POST", path="/another", must_be_authenticated=False)
async def another_route(req):
    res = await db_fns.ac_user_create_pw("test@test.com", "a1s2d3f4g5", {"random": "stuff"})
    return {"hi": res}
