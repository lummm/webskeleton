from typing import Dict, List, Literal, NamedTuple, Union, Tuple

from aiohttp import web  # type: ignore
from box import Box  # type: ignore


class ReplyOperation(NamedTuple):
    fn: Union[Literal["set_cookie"]]
    args: List
    kwargs: Dict


ERR_STATUS_MAP = {
    400: web.HTTPBadRequest,
    401: web.HTTPUnauthorized,
    403: web.HTTPForbidden,
}


class Req:
    q_params: Box
    params: Box
    wrapped: web.Request
    user_id: str
    reply_operations: List[ReplyOperation]
    reply_headers: List[Tuple[str, str]]

    def __init__(
        self,
        *,
        wrapped: web.Request,
        params: Box = Box(),
    ):
        self.wrapped = wrapped
        self.params = params
        self.reply_operations = []
        self.reply_headers = []
        return

    def fail(self, status: int, msg: str = "") -> Exception:
        if status in ERR_STATUS_MAP:
            return ERR_STATUS_MAP[status](text=msg)
        return web.HTTPInternalServerError(text=msg)

    def set_cookie(self, *, name: str, value: str, path: str, httponly: bool = True):
        self.reply_operations.append(
            ReplyOperation(
                fn="set_cookie",
                args=[name, value],
                kwargs={"path": path, "httponly": httponly},
            )
        )
        return
