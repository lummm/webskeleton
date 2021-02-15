from webskeleton import routedef, Req


@routedef(
    method="GET",
    path="/",
    must_be_authenticated=False,
)
async def entry(req: Req):
    return "OK"
