import requests
BASE_URL = "http://127.0.0.1:3000/rest"

def test_login_success():
    """正向登录成功，校验返回token"""
    payload = {"email": "admin@juice-sh.op", "password": "admin123"}
    res = requests.post(f"{BASE_URL}/user/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "token" in data["authentication"]

def test_login_wrong_pwd():
    """错误密码登录，校验返回401"""
    payload = {"email": "admin@juice-sh.op", "password":"wrong123"}
    res = requests.post(f"{BASE_URL}/user/login", json=payload)
    assert res.status_code == 401
