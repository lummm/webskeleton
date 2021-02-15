import json

import requests


s = requests.Session()

url_base = "http://localhost:8888"


def req(method: str, url: str, data = None):
    return s.request(
        method,
        f"{url_base}{url}",
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


def test_login():
    res = req("POST", "/login", {"username": "test", "password": "a1s2d3f4g5"})
    assert res.status_code == 200
    print(res.json())
    return
