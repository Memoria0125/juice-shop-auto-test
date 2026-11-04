import base64
import json
import time
from dataclasses import dataclass
from typing import Any

import allure
import requests


SENSITIVE_KEYS = {"authorization", "password", "token"}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "***" if key.lower() in SENSITIVE_KEYS else sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def decode_jwt_claims(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise AssertionError("登录返回的 Token 不是合法的三段式 JWT")
    padded = parts[1] + "=" * (-len(parts[1]) % 4)
    return json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))


@dataclass(frozen=True)
class Settings:
    base_url: str
    email: str
    password: str
    timeout: float


@dataclass(frozen=True)
class AuthContext:
    token: str
    basket_id: int
    claims: dict

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        started = time.perf_counter()
        with allure.step(f"{method.upper()} {path}"):
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            payload = sanitize(kwargs.get("json") or kwargs.get("params") or {})
            allure.attach(
                json.dumps(payload, ensure_ascii=False, indent=2),
                name="请求参数（敏感字段已脱敏）",
                attachment_type=allure.attachment_type.JSON,
            )

            try:
                response_body = sanitize(response.json())
                attachment_type = allure.attachment_type.JSON
                body_text = json.dumps(response_body, ensure_ascii=False, indent=2)
            except ValueError:
                attachment_type = allure.attachment_type.TEXT
                body_text = response.text

            allure.attach(
                body_text[:8000],
                name=f"响应 {response.status_code} · {elapsed_ms} ms（敏感字段已脱敏）",
                attachment_type=attachment_type,
            )
        return response

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def close(self) -> None:
        self.session.close()
