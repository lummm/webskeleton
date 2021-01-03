import asyncio
import functools
from inspect import getmembers, isfunction
import json
from multidict import MultiDictProxy
from types import ModuleType
from typing import Any, cast, Dict, List, NamedTuple, Optional, Tuple, Union

from aiohttp import web  # type: ignore
from box import Box  # type: ignore

from . import auth
from . import db
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


def req_wrapper_factory():
    @web.middleware
    async def wrap_req(request, handler):
        req = Req(wrapped=request)
        return await handle_json(req, handler)

    return wrap_req


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

        impl_fn.is_endpoint = True
        impl_fn.path = path
        impl_fn.method = method
        return impl_fn

    return dec


def load_routes(webapp: web.Application, routes_mod: ModuleType) -> web.Application:
    METHOD_MAP = {
        "GET": web.get,
        "POST": web.post,
        "PUT": web.put,
    }
    fns = [f for name, f in getmembers(routes_mod)
           if isfunction(f) and getattr(f,"is_endpoint", None)]
    routes = [
        METHOD_MAP[fn.method](fn.path, fn) # type: ignore
        for fn in fns
    ]
    webapp.add_routes(routes)
    return webapp




class WebSkeleton():
    def __init__(self, routes_module: ModuleType):
        self.routes_module = routes_module
        return

    def run(
            self,
            *,
            port: int = 0,
            dbuser: str = "postgres",
            dbpassword: str = "",
            database: str = "postgres",
            dbhost: str = "127.0.0.1",
    ):
        import uvloop           # type: ignore
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        async def init():
            await db.connect(user=dbuser, password=dbpassword, database=database, host=dbhost)
            app = web.Application(middlewares=[req_wrapper_factory()])
            app = load_routes(app, self.routes_module)
            return app

        web.run_app(init(), port=port)
        return
