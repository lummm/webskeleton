import requests


s = requests.Session()

def test_basic():
    res = s.get("http://localhost:8888/")
    print(res)
    return
