"""
This handles auth related logic.
TODO: rename this into private and public.
"""
import base64
import logging
import os
import re
import time
from typing import (
    Dict,
)

import jwt
from jwt.exceptions import InvalidTokenError  # type: ignore

from . import autheval
from . import appredis
from .env import ENV
from .request import Req
from .typez import AuthPolicy, AuthConf


BEARER_REGEX = re.compile("^Bearer (.*)$")
REFRESH_TOKEN_COOKIE = "webskeleton-refresh"

TOKEN_ALGO = "HS256"


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


def issue_access_token(user_id: str) -> str:
    "creates a jwt with user_id as payload"
    exp_time = time.time() + ENV.ACCESS_TOKEN_EXP_S
    return jwt.encode(
        {
            "exp": exp_time,
            "user_id": user_id,
        },
        ENV.KEY,
        algorithm=TOKEN_ALGO,
    )


async def issue_refresh_token(
    user_id: str,
    req: Req,
) -> str:
    """
    Creates a random string refresh token.
    The token is saved in Redis with an expire time
    of REFRESH_TOKEN_EXP_S seconds,
    and set as an hhtp-only cookie on the request.
    """
    # can also delete existing tokens
    token = base64.b64encode(os.urandom(ENV.REFRESH_TOKEN_SIZE)).decode("utf-8")
    await appredis.set_str(token, user_id, ENV.REFRESH_TOKEN_EXP_S)
    req.set_cookie(name=REFRESH_TOKEN_COOKIE, value=token, path="/")
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
    claims = parse_token(ENV.KEY, token)
    return claims


async def attempt_lookup_refresh_token(
    req: Req,
) -> str:
    """
    Look up the refresh token.
    If found, we generate a new refresh token,
    deleting the old one.
    The new token will be updated as a cookie.
    We return the user id.
    """
    refresh_token = req.wrapped.cookies[REFRESH_TOKEN_COOKIE]
    if not refresh_token:
        raise CredsParseException("no refresh token")
    user_id = await appredis.get_str(refresh_token)
    if not user_id:
        raise CredsParseException("invalid refresh token")
    await issue_refresh_token(user_id, req)
    await appredis.delete(refresh_token)
    return user_id


async def check_authenticated(req: Req) -> str:
    auth_header = req.wrapped.headers.get("authorization")
    if not auth_header:
        raise req.fail(401, "no 'authorization' header")
    try:
        claims = creds_parse_bearer(auth_header)
        return claims["user_id"]
    except CredsParseException as access_e:
        logging.error("creds parse failed - %s", access_e)
        try:
            user_id = await attempt_lookup_refresh_token(req)
            logging.info("refreshing session for %s", user_id)
            access_token = issue_access_token(user_id)
            req.reply_headers.append(("set-session-token", access_token))

            return user_id
        except CredsParseException:
            raise req.fail(401, "invalid access token and invalid refresh token")
    return


async def check_authorized_policy(req: Req, auth_conf: AuthConf) -> bool:
    obj_ids = auth_conf.obj_ids and auth_conf.obj_ids(req)
    handler = get_handler(auth_conf.policy, req)
    if not await handler(req.user_id, obj_ids):
        raise req.fail(403, f"auth check failed for user: {auth_conf}")
    return True
