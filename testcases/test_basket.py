import allure
import pytest

from framework.api_client import ApiClient, AuthContext


@allure.epic("Juice Shop API 自动化")
@allure.feature("购物篮鉴权")
class TestBasketAuthorization:
    @pytest.mark.auth
    @pytest.mark.smoke
    @allure.story("合法 Token")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("合法 Token 可以读取本人购物篮")
    def test_get_own_basket(self, client: ApiClient, auth_context: AuthContext):
        response = client.get(
            f"/rest/basket/{auth_context.basket_id}",
            headers=auth_context.headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["id"] == auth_context.basket_id
        assert body["data"]["UserId"] == auth_context.claims["data"]["id"]
        assert isinstance(body["data"]["Products"], list)

    @pytest.mark.auth
    @allure.story("匿名访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("匿名请求购物篮被拒绝")
    def test_basket_rejects_anonymous_request(
        self,
        client: ApiClient,
        auth_context: AuthContext,
    ):
        response = client.get(f"/rest/basket/{auth_context.basket_id}")
        assert response.status_code == 401

    @pytest.mark.auth
    @allure.story("非法 Token")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("非法 Token 请求购物篮被拒绝")
    def test_basket_rejects_invalid_token(
        self,
        client: ApiClient,
        auth_context: AuthContext,
    ):
        response = client.get(
            f"/rest/basket/{auth_context.basket_id}",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
