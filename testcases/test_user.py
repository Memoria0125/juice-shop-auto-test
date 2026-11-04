import allure
import pytest

from framework.api_client import ApiClient, AuthContext, Settings


@allure.epic("Juice Shop API 自动化")
@allure.feature("用户认证")
class TestUserLogin:
    @pytest.mark.auth
    @pytest.mark.smoke
    @allure.story("登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("正确账号和密码登录成功并返回 JWT")
    def test_login_success(self, auth_context: AuthContext):
        assert auth_context.token
        assert auth_context.token.count(".") == 2
        assert auth_context.basket_id > 0

    @pytest.mark.auth
    @allure.story("JWT 内容")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("JWT 包含正确的用户、角色和购物篮信息")
    def test_login_token_claims(self, settings: Settings, auth_context: AuthContext):
        user = auth_context.claims["data"]
        assert user["email"] == settings.email
        assert user["role"] == "admin"
        assert auth_context.claims["bid"] == auth_context.basket_id

    @pytest.mark.auth
    @allure.story("登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("错误密码返回 401 且不下发 Token")
    def test_login_wrong_password(self, client: ApiClient, settings: Settings):
        response = client.post(
            "/rest/user/login",
            json={"email": settings.email, "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert "authentication" not in response.text.lower()
