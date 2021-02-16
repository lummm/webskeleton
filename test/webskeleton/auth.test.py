import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call

from aiohttp import web
from box import Box
import jwt

from webskeleton import AuthConf, Req
import webskeleton.auth as auth


user_id = "test-user-id"


class AuthTest(IsolatedAsyncioTestCase):
    def test_issue_access_token(self):
        req = Req(wrapped=None)
        token = auth.issue_access_token(user_id, req)
        self.assertEqual(
            req.reply_headers,
            [(auth.SET_SESSION_TOKEN_HEADER, token)]
        )
        return

    def test_issue_and_parse_creds(self):
        req = Req(wrapped=None)
        token = auth.issue_access_token(user_id, req)
        bearer_creds = f"Bearer {token}"
        claims = auth.creds_parse_bearer(bearer_creds)
        self.assertEqual(claims["user_id"], user_id)
        return

    async def test_issue_refresh_token(self):
        import webskeleton.appredis as appredis
        appredis.set_str = AsyncMock()
        req = Req(wrapped=None)
        req.set_cookie = MagicMock()
        token = await auth.issue_refresh_token(user_id, req)
        save_call = appredis.set_str.call_args_list[0]
        self.assertEqual(save_call.args[0], token)
        self.assertEqual(save_call.args[1], user_id)
        self.assertEqual(
            req.set_cookie.call_args[-1], {
                "name": auth.REFRESH_TOKEN_COOKIE,
                "value": token,
                "path": "/",
            }
        )
        return

    async def test_check_authorized_policy(self):
        import webskeleton.autheval as autheval
        request_objects = ["obj-1"]
        req = Req(wrapped = None)
        req.user_id = "test-user-id"
        auth_conf = AuthConf(
            policy = "user-owns",
            obj_ids = lambda _req: request_objects,
        )
        autheval.user_owns_all = AsyncMock(
            return_value=True
        )
        self.assertTrue(
            await auth.check_authorized_policy(
                req, auth_conf)
        )
        auth_eval_call = autheval.user_owns_all.call_args_list[0]
        self.assertEqual(
            auth_eval_call.args[0],
            req.user_id,
        )
        self.assertEqual(
            auth_eval_call.args[1],
            request_objects,
        )
        autheval.user_owns_all = AsyncMock(
            return_value=False
        )
        with self.assertRaises(web.HTTPForbidden):
            await auth.check_authorized_policy(
                req, auth_conf)
        return

    async def test_attempt_lookup_refresh_token(self):
        import webskeleton.appredis as appredis
        refresh_token = "a1s2d3f4"
        req = Req(
            wrapped=Box({
                "cookies": {
                    auth.REFRESH_TOKEN_COOKIE: refresh_token,
                },
            })
        )
        user_id = "test-user-id"
        appredis.get_str = AsyncMock(return_value=user_id)
        appredis.set_str = AsyncMock()
        appredis.delete = AsyncMock()
        lookup_user_id = await auth.attempt_lookup_refresh_token(req)
        self.assertEqual(
            appredis.get_str.call_args_list[0].args[0],
            refresh_token,
        )
        self.assertEqual(
            appredis.delete.call_args_list[0].args[0],
            refresh_token,
        )
        self.assertEqual(lookup_user_id, user_id)
        return


if __name__ == '__main__':
    unittest.main()
