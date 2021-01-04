import base64
import logging
import os
import re
import time
from typing import (
    Any,
    Dict,
    NamedTuple,
    Optional,
    Union,
    Callable,
    List,
    Literal,
    Tuple,
)

import jwt
from jwt.exceptions import InvalidTokenError  # type: ignore

from . import autheval
from . import appredis
from .request import Req
from .typez import AuthPolicy, TokenType, AuthConf


BEARER_REGEX = re.compile("^Bearer: (.*)$")
# I added another header called 'refresh'

key = ""
with open("./key", "r") as f:
    key = f.read()


TOKEN_ALGO = "HS256"
REFRESH_TOKEN_SIZE = 24
ACCESS_TOKEN_EXP_S = 1800  # 30 mins
REFRESH_TOKEN_EXP_S = 259200  # 3 days


class CredsParseException(Exception):
    pass


def parse_token(
    token_sig: str,
    token: str,
) -> Dict:
    try:
        claims = jwt.decode(token, token_sig, algorithms=[TOKEN_ALGO])
    except InvalidTokenError as e:
        logging.error("jwt parse failed: %s", e)
        raise CredsParseException("token parse failed")
    return claims


def set_access_token_exp_s(seconds: int) -> None:
    global ACCESS_TOKEN_EXP_S
    ACCESS_TOKEN_EXP_S = seconds
    return


def set_refresh_token_exp_s(seconds: int) -> None:
    global REFRESH_TOKEN_EXP_S
    REFRESH_TOKEN_EXP_S = seconds
    return


def issue_access_token(user_id: str) -> str:
    exp_time = time.time() + ACCESS_TOKEN_EXP_S
    return jwt.encode(
        {
            "exp": exp_time,
            "user_id": user_id,
        },
        key,
        algorithm=TOKEN_ALGO,
    ).decode("utf-8")


async def issue_refresh_token(
    user_id: str,
) -> str:
    token = base64.b64encode(os.urandom(REFRESH_TOKEN_SIZE)).decode("utf-8")
    await appredis.set_str(token, user_id, REFRESH_TOKEN_EXP_S)
    return token


def get_handler(policy: AuthPolicy, req: Req):
    if policy == "user-owns":
        return autheval.user_owns_all
    raise Exception("no known auth handler")


def creds_parse_bearer(
    bearer_creds: str,
) -> Dict:  # claims
    match = re.match(BEARER_REGEX, bearer_creds)
    if not match:
        raise CredsParseException("failed to parse token from creds")
    token = match.groups()[0]
    if not token:
        raise CredsParseException("bad creds")
    claims = parse_token(key, token)
    return claims


async def attempt_lookup_refresh_token(
    req: Req,
) -> Tuple[str, str,]:  # user_id  # refresh_token
    refresh_header = req.wrapped.headers.get("refresh")
    if not refresh_header:
        raise CredsParseException("no refresh token")
    user_id = await appredis.get_str(refresh_header)
    if not user_id:
        raise CredsParseException("invalid refresh token")
    new_refresh_token = await issue_refresh_token(user_id)
    await appredis.pool.delete(refresh_header)
    return (user_id, new_refresh_token)


async def check_authenticated(req: Req) -> str:
    auth_header = req.wrapped.headers.get("authorization")
    if not auth_header:
        raise req.fail(401, "no 'authorization' header")
    try:
        claims = creds_parse_bearer(auth_header)
        return claims["user_id"]
    except CredsParseException as access_e:
        try:
            user_id, refresh_token = await attempt_lookup_refresh_token(req)
            logging.info("refreshing session for %s", user_id)
            access_token = issue_access_token(user_id)
            req.reply_headers.append(("set-session-token", access_token))
            req.reply_headers.append(("set-refresh-token", refresh_token))
            return user_id
        except CredsParseException:
            raise req.fail(401, "invalid access token and invalid refresh token")
    return


async def check_authorized_policy(req: Req, auth_conf: AuthConf) -> bool:
    obj_ids = auth_conf.obj_ids and auth_conf.obj_ids(req)
    handler = get_handler(auth_conf.policy, req)
    if not await handler(req.user_id, obj_ids):
        raise req.fail(403, f"unauthorized failed for user: {auth_conf}")
    return True
