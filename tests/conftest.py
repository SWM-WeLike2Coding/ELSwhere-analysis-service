from unittest.mock import patch, AsyncMock
import pytest

# 최초기준가격 대비 현재 기초자산가격 비율 api 테스트 데이터를 위한 fixture
@pytest.fixture
def mock_product_response():
    return {
        "initialBasePriceEvaluationDate": "2024-07-12",
        "equities": "KOSPI200 Index / S&P500 Index / Euro Stoxx 50 Index",
        "equityTickerSymbols": {
            "KOSPI200 Index": "^KS200",
            "S&P500 Index": "^GSPC",
            "Euro Stoxx 50 Index": "^STOXX50E"
        }
    }

# yfinance Ticker 클래스의 모킹을 위한 fixture
# 내부에서 yfinance.Ticker 구문이 실행되면 mock 객체로 전환
@pytest.fixture
def mock_ticker():
    with patch('yfinance.Ticker') as mock:
        yield mock

# eureka_client의 do_service_async를 모킹하기 위한 fixture
# 내부에서 py_eureka_client.eureka_client.do_service_async 구문이 실행되면 mock 객체로 전환
@pytest.fixture
def mock_do_service_async():
    with patch('py_eureka_client.eureka_client.do_service_async', new_callable=AsyncMock) as mock:
        yield mock