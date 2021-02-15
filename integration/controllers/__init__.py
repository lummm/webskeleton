from webskeleton import (
    routedef,
    Req,
    issue_access_token,
    issue_refresh_token,
)



@routedef(
    method="GET",
    path="/",
    must_be_authenticated=False,
)
async def entry(req: Req):
    return "OK"


@routedef(
    method="GET",
    path="/no_authenticate",
)
async def no_authenticate(req: Req):
    return "OK"


@routedef(
    method="POST",
    path="/login",
    must_be_authenticated=False,
    params=[
        "username",
        "password",
    ],
)
async def login(req: Req):
    user_id = "test"
    access_token = issue_access_token(user_id)
    refresh_token = await issue_refresh_token(user_id, req)
    return {
        "access": access_token,
    }
