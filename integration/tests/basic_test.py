import json

import requests


s = requests.Session()

url_base = "http://localhost:8888"


def req(method: str, url: str, data = None, headers = {}):
    return s.request(
        method,
        f"{url_base}{url}",
        headers=headers,
        **({"data": json.dumps(data)} if data else {}),
    )


def test_basic():
    res = req("GET", "/")
    assert res.status_code == 200
    assert res.json() == "OK"
    return


def test_unauth():
    res = req("GET", "/no_authenticate")
    assert res.status_code == 401
    return


def test_login_no_params():
    res = req("POST", "/login")
    assert res.status_code == 400
    return


def test_login_basic():
    res = req("POST", "/login", {"username": "test", "password": "a1s2d3f4g5"})
    assert res.status_code == 200
    return


def test_login_and_refresh():
    res = req("POST", "/login", {"username": "test", "password": "a1s2d3f4g5"})
    assert res.status_code == 200
    res = req("POST", "/needs-auth", headers={"Authorization": "nope"}) # need the header to trigger refresh token usage
    assert res.status_code == 200
    session_token = res.headers["set-session-token"]
    assert session_token is not None
    auth_header = f"Bearer {session_token}"
    res = req("POST", "/needs-auth", headers={"Authorization": auth_header})
    assert res.status_code == 200
    # when we supply the session token, we don't expect a new session token,
    # unless ours has expired (which it won't have in the last millisecond)
    assert "set-session-token" not in res.headers
    return
