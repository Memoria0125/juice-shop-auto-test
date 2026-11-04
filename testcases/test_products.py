import allure
import pytest

from framework.api_client import ApiClient


@allure.epic("Juice Shop API 自动化")
@allure.feature("商品目录")
class TestProducts:
    @pytest.mark.contract
    @pytest.mark.smoke
    @allure.story("商品列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("商品列表返回成功且字段结构正确")
    def test_product_catalog_contract(self, client: ApiClient):
        response = client.get("/api/Products")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert isinstance(body["data"], list)
        assert body["data"], "商品目录不应为空"

        product = body["data"][0]
        assert isinstance(product["id"], int)
        assert product["name"]
        assert isinstance(product["price"], (int, float))
        assert product["price"] >= 0

    @pytest.mark.contract
    @allure.story("商品详情")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("按商品 ID 查询详情成功")
    def test_product_detail(self, client: ApiClient):
        response = client.get("/api/Products/1")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["id"] == 1
        assert body["data"]["name"]

    @pytest.mark.contract
    @allure.story("商品搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("关键字搜索能返回匹配商品")
    def test_search_products_by_keyword(self, client: ApiClient):
        response = client.get("/rest/products/search", params={"q": "apple"})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert isinstance(body["data"], list)
        assert any("apple" in item["name"].lower() for item in body["data"])

    @pytest.mark.contract
    @allure.story("商品搜索")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("无匹配关键字返回空列表")
    def test_search_products_without_match(self, client: ApiClient):
        response = client.get(
            "/rest/products/search",
            params={"q": "product-that-does-not-exist-2026"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"] == []
