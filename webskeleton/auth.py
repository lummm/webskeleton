import logging
import re
import time
from typing import Any, Dict, NamedTuple, Optional, Union, Callable, List
from typing_extensions import Literal

import jwt

from .request import Req
from .typez import AuthPolicy, TokenType, AuthConf


BEARER_REGEX = re.compile("^Bearer: (.*)$")

key = ""
with open("./key", "r") as f:
    key = f.read()


TOKEN_ALGO = "HS256"


class CredsParseException(Exception):
    pass


def parse_token(
    token_sig: str,
    token: str,
    token_type: str,
) -> Dict:
    claims = jwt.decode(token, token_sig, algorithms=[TOKEN_ALGO])
    if claims["token_type"] != token_type:
        raise CredsParseException("bad token type")
    return claims


def issue_token(
    *,
    user_id: str,
    token_type: str,
    exp_s: int,
    token_sig: str,
) -> str:
    exp_time = time.time() + exp_s
    return jwt.encode(
        {
            "exp": exp_time,
            "user_id": user_id,
            "token_type": token_type,
        },
        token_sig,
        algorithm=TOKEN_ALGO,
    ).decode("utf-8")


def get_handler(policy: AuthPolicy, req: Req):
    if policy == "user-owns":
        return True
        # return req.services.authorize.user_owns_all
    raise Exception("no known auth handler")


def creds_parse_bearer(
        bearer_creds: str,
        token_type: TokenType,
) -> Dict:  # claims
        match = re.match(BEARER_REGEX, bearer_creds)
        if not match:
            raise CredsParseException("failed to parse token from creds")
        token = match.groups()[0]
        if not token:
            raise CredsParseException("bad creds")
        claims = parse_token(key, token, token_type)
        return claims


async def check_authenticated(req: Req) -> str:
    auth_header = req.wrapped.headers.get("authorization")
    if not auth_header:
        raise req.fail(401, "no 'authorization' header")
    claims = await req.creds_parse_bearer(auth_header, "session")
    if not claims:
        raise req.fail(401, "bad 'authorization' header")
    return claims["user_id"]


async def check_authorized_policy(req: Req, auth_conf: AuthConf) -> bool:
    obj_ids = auth_conf.obj_ids and auth_conf.obj_ids(req)
    handler = get_handler(auth_conf.policy, req)
    if not await handler(req.user_id, obj_ids):
        raise req.fail(403, f"unauthorized failed for user: {auth_conf}")
    return True
