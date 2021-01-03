import asyncio
import functools
from inspect import getmembers, isfunction
import json
from multidict import MultiDictProxy
from types import ModuleType
from typing import Any, cast, Dict, List, NamedTuple, Optional, Tuple, Union

from aiohttp import web  # type: ignore
from box import Box  # type: ignore

from .typez import AuthConf, Req


ParamConf = Union[str, Tuple[str, Any]]  # key, or key and default


def get_param_and_val(
    param: ParamConf, container: Union[Dict, MultiDictProxy[str]], container_type: str
) -> Tuple[str, Any]:
    if type(param) == str:
        name: str = cast(str, param)
        if name not in container:
            raise web.HTTPBadRequest(body=f"missing {container_type} parameter {name}")
        return (name, container.get(name))
    name, default = cast(Tuple[str, Any], param)
    if name not in container:
        return (name, default)
    return (name, container.get(name))


async def read_body_params(request: web.Request, params: List[ParamConf]) -> Box:
    if not request.can_read_body:
        raise web.HTTPBadRequest(body="request requires body")
    body = await request.json()
    return Box(get_param_and_val(param, body, "body") for param in params)


async def handle_json(req: Req, handler) -> web.Response:
    response_body = None
    try:
        response_body = await handler(req)
    except web.HTTPException as e:
        return web.Response(status=e.status, text=e.text)
    res = web.Response()
    if getattr(response_body, "_asdict", None):  # a namedtuple
        res.text = json.dumps(response_body._asdict())
    else:
        res.text = json.dumps(response_body)
    for action in req.reply_operations:
        getattr(res, action.fn)(*action.args, **action.kwargs)
    return res


def wrap_req_factory(services: Services):
    @web.middleware
    async def wrap_req(request, handler):
        req = Req(wrapped=request, services=services)
        return await handle_json(req, handler)

    return wrap_req


def init_webapp() -> web.Application:
    app = web.Application(middlewares=[wrap_req_factory(app_services)])
    return app


# public
def routedef(
    method="GET",
    path="",
    params: List[ParamConf] = [],
    q_params: List[ParamConf] = [],
    must_be_authenticated=True,
    auth_conf: Optional[AuthConf] = None,
):
    """
    decorator to define a route
    """
    def dec(fn):
        @functools.wraps(fn)
        async def impl_fn(req: Req):
            if params:
                req.params = await read_body_params(req.wrapped, params)
            if q_params:
                req.q_params = Box(
                    get_param_and_val(param, req.wrapped.query, "query")
                    for param in q_params
                )
            if must_be_authenticated:
                user_id = await auth.check_authenticated(req)
                req.user_id = user_id
            if auth_conf:
                await auth.check_authorized_policy(req, auth_conf)
            return await fn(req)

        # route_list.append(METHOD_MAP[method](path, impl_fn))
        impl_fn.is_endpoint = True
        impl_fn.path = path
        impl_fn.method = method
        return impl_fn

    return dec


class WebSkeleton():
    def __init__(self, webapp: web.Application):
        self.webapp = webapp
        return


    def run(self, port: int):
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        web.run_app(webapp, port=port)
        return


def load_routes(routes_mod: ModuleType) -> WebSkeleton:
    webapp = init_webapp()
    METHOD_MAP = {
        "GET": web.get,
        "POST": web.post,
        "PUT": web.put,
    }
    fns = [isfunction(f) and getattr(f,"is_endpoint", None)
           for name, f in getmembers(routes_mod)]
    routes = [
        METHOD_MAP[fn.method](fn.path, fn)
        for fn in fns
    ]
    webapp.add_routes(routes)
    return WebSkeleton(webapp=webapp)
