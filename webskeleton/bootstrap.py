import asyncio
from inspect import getmembers, isfunction
import json
import logging
from types import ModuleType

from aiohttp import web  # type: ignore

from . import appredis
from . import db
from .env import ENV
from .typez import Req


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
    for key, val in req.reply_headers:
        res.headers[key] = val
    return res


def req_wrapper_factory():
    @web.middleware
    async def wrap_req(request, handler):
        req = Req(wrapped=request)
        return await handle_json(req, handler)

    return wrap_req


# public
def load_routes(webapp: web.Application, routes_mod: ModuleType) -> web.Application:
    METHOD_MAP = {
        "GET": web.get,
        "POST": web.post,
        "PUT": web.put,
    }
    fns = [
        f
        for name, f in getmembers(routes_mod)
        if isfunction(f) and getattr(f, "is_endpoint", None)
    ]
    routes = [METHOD_MAP[fn.method](fn.path, fn) for fn in fns]  # type: ignore
    logging.info("loaded routes:\n%s", "\n".join(map(str, routes)))
    webapp.add_routes(routes)
    return webapp


class WebSkeleton:
    def __init__(self, routes_module: ModuleType):
        self.routes_module = routes_module
        return

    def run(self):
        import uvloop  # type: ignore

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        async def init():
            await db.connect()
            await appredis.connect()
            app = web.Application(middlewares=[req_wrapper_factory()])
            app = load_routes(app, self.routes_module)
            return app

        web.run_app(init(), port=ENV.PORT)
        return
