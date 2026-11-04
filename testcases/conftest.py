import os
import platform
from pathlib import Path

import allure
import pytest

from framework.api_client import (
    ApiClient,
    AuthContext,
    Settings,
    decode_jwt_claims,
)


@pytest.fixture(scope="session")
def settings() -> Settings:
    base_url = os.getenv("JUICE_SHOP_URL", "http://127.0.0.1:3000").rstrip("/")
    return Settings(
        base_url=base_url,
        email=os.getenv("JUICE_SHOP_EMAIL", "admin@juice-sh.op"),
        password=os.getenv("JUICE_SHOP_PASSWORD", "admin123"),
        timeout=float(os.getenv("JUICE_SHOP_TIMEOUT", "10")),
    )


@pytest.fixture(scope="session")
def client(settings: Settings):
    api_client = ApiClient(settings.base_url, settings.timeout)
    yield api_client
    api_client.close()


@pytest.fixture(scope="session")
def auth_context(client: ApiClient, settings: Settings) -> AuthContext:
    with allure.step("使用测试账号登录并获取 JWT Token"):
        response = client.post(
            "/rest/user/login",
            json={"email": settings.email, "password": settings.password},
        )
        assert response.status_code == 200, response.text
        authentication = response.json()["authentication"]
        token = authentication["token"]
        return AuthContext(
            token=token,
            basket_id=int(authentication["bid"]),
            claims=decode_jwt_claims(token),
        )


def pytest_sessionfinish(session, exitstatus):
    allure_dir = getattr(session.config.option, "allure_report_dir", None)
    if not allure_dir:
        return

    target = os.getenv("JUICE_SHOP_URL", "http://127.0.0.1:3000").rstrip("/")
    lines = [
        f"Target={target}",
        f"Python={platform.python_version()}",
        f"Platform={platform.platform()}",
        "Test-Framework=pytest + requests",
        f"Exit-Code={exitstatus}",
    ]
    output_dir = Path(allure_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "environment.properties").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )
