from webskeleton import routedef


@routedef(method="GET", path="/big")
def big_route(req):
    return {"hi": 3}


@routedef(method="POST", path="/another")
def another_route(req):
    return {"hi": 2}
