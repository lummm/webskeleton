import functools
from typing import Any, cast, Dict, List, Optional, Tuple, Union


from aiohttp import web  # type: ignore
from box import Box  # type: ignore
from multidict import MultiDictProxy

from . import auth
from .typez import AuthConf, Req


ParamConf = Union[str, Tuple[str, Any]]  # key, or key and default


def get_param_and_val(
    param: ParamConf, container: Union[Dict, MultiDictProxy[str]], container_type: str
) -> Tuple[str, Any]:
    if type(param) == str:
        name: str = cast(str, param)
        if name not in container:
            raise web.HTTPBadRequest(text=f"missing {container_type} parameter {name}")
        return (name, container.get(name))
    name, default = cast(Tuple[str, Any], param)
    if name not in container:
        return (name, default)
    return (name, container.get(name))


async def read_body_params(request: web.Request, params: List[ParamConf]) -> Box:
    if not request.can_read_body:
        raise web.HTTPBadRequest(text="request requires body")
    body = await request.json()
    return Box(get_param_and_val(param, body, "body") for param in params)


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
