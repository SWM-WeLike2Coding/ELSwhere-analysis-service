from httpx import AsyncClient, ASGITransport
from exception.errors import ProductServiceServerException
from main import app
import pytest
import pandas as pd
import json

# 최초기준가격 대비 현재 기초자산가격 비율 - 상품 API 호출이 성공할 때의 최초기준가격 대비 현재 기초자산가격 비율 테스트 케이스
@pytest.mark.asyncio
async def test_get_price_ratio_success(mock_do_service_async, mock_product_response, mock_ticker):
    mock_do_service_async.return_value = json.dumps(mock_product_response)

    mock_ticker_instance = mock_ticker.return_value
    # 요청에 따라 순서 대로 반환
    mock_ticker_instance.history.side_effect = [
        pd.DataFrame({"Close": [150.0]}, index=pd.to_datetime(["2024-07-12"])),
        pd.DataFrame({"Close": [280.0]}, index=pd.to_datetime(["2024-07-12"])),
        pd.DataFrame({"Close": [300.0]}, index=pd.to_datetime(["2024-07-12"])),

        pd.DataFrame({"Close": [160.0]}, index=pd.to_datetime(["2024-08-21"])),
        pd.DataFrame({"Close": [300.0]}, index=pd.to_datetime(["2024-08-21"])),
        pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2024-08-21"]))
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/product/price/ratio/1")

    assert response.status_code == 200
    response_json = response.json()
    assert "initial" in response_json
    assert "recent" in response_json
    assert "ratio" in response_json
    assert "recentAndInitialPriceRatio" in response_json
    assert response_json["initial"]["KOSPI200 Index"] == 150.0
    assert response_json["recent"]["KOSPI200 Index"] == 160.0
    assert response_json["ratio"]["KOSPI200 Index"] == 106.67
    assert response_json["recentAndInitialPriceRatio"] == -66.67


# 최초기준가격 대비 현재 기초자산가격 비율 - 상품 API 호출이 실패할 때의 테스트 케이스
@pytest.mark.asyncio
async def test_get_price_ratio_failure(mock_do_service_async):
    mock_do_service_async.side_effect = ProductServiceServerException(productId=123)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/product/price/ratio/1")

    assert response.status_code == 500
    response_json = response.json()
    assert response_json["status_code"] == 500
    assert response_json["code"] == "ProductServiceServerException"
    assert response_json["message"] == "상품 서비스와 통신 중 문제가 발생하였습니다."
    assert "timestamp" in response_json
    assert "trackingId" in response_json
