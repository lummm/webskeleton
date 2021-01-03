from webskeleton import routedef


@routedef(method="GET", path="/big")
async def big_route(req):
    return {"hi": 3}


@routedef(method="POST", path="/another", must_be_authenticated=False)
async def another_route(req):
    return {"hi": 2}
