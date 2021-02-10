import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call

import jwt

import webskeleton.auth as auth


class AuthTest(IsolatedAsyncioTestCase):
    def test_issue_access_token(self):
        user_id = "test-user-id"
        token = auth.issue_access_token(user_id)
        return

    def test_issue_and_parse_creds(self):
        user_id = "test-user-id"
        token = auth.issue_access_token(user_id)
        bearer_creds = f"Bearer {token}"
        claims = auth.creds_parse_bearer(bearer_creds)
        self.assertEqual(claims["user_id"], user_id)
        return


if __name__ == '__main__':
    unittest.main()
