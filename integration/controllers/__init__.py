from webskeleton import routedef, Req


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
    must_be_authenticated=True,
)
async def no_authenticate(req: Req):
    return "OK"
