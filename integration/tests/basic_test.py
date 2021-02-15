import requests


s = requests.Session()

url_base = "http://localhost:8888"


def req(method: str, url: str, data = None):
    return s.request(
        method,
        f"{url_base}{url}",
        **({"data": data} if data else {}),
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
