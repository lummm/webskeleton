import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call

import jwt

import webskeleton.auth as auth


user_id = "test-user-id"


class AuthTest(IsolatedAsyncioTestCase):
    def test_issue_access_token(self):
        token = auth.issue_access_token(user_id)
        return

    def test_issue_and_parse_creds(self):
        token = auth.issue_access_token(user_id)
        bearer_creds = f"Bearer {token}"
        claims = auth.creds_parse_bearer(bearer_creds)
        self.assertEqual(claims["user_id"], user_id)
        return

    async def test_issue_refresh_token(self):
        import webskeleton.appredis as appredis
        appredis.set_str = AsyncMock()
        token = await auth.issue_refresh_token(user_id)
        save_call = appredis.set_str.call_args_list[0]
        self.assertEqual(save_call.args[0], token)
        self.assertEqual(save_call.args[1], user_id)
        return


if __name__ == '__main__':
    unittest.main()
