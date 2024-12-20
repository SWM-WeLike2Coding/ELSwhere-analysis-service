from fastapi import APIRouter, Path, Request
from typing import Dict, List
from pydantic import BaseModel, RootModel
from exception.errors import ProductServiceServerException, ValidateInitialBasePriceEvaluationDateException
from exception.error_response_examples import product_service_exception_response, validate_initial_price_exception_response
from datetime import datetime
from typing import Optional
import py_eureka_client.eureka_client as eureka_client
import pandas as pd
import json
import urllib.error
import yfinance as yf
import asyncio

router = APIRouter()

class PriceData(RootModel[Dict[str, float]]):
    pass
class PriceRatioResponse(BaseModel):
    initial: PriceData
    recent: PriceData
    ratio: PriceData
    recentAndInitialPriceRatio: float
class ProductIdListModel(BaseModel):
    productIdList: List[int]
class PriceRatio(BaseModel):
    id: int
    recentAndInitialPriceRatio: Optional[float]

@router.get("/price/ratio/{productId}",
            summary="상품 단건에 대한 최초기준가격 대비 현재 기초자산가격 비율 조회",
            description="""
                            각 상품에 존재하는 기초자산들의 최초기준가격 대비 현재 기초자산가격 비율 정보들을 제공합니다.<br/>
                            이 비율 정보들을 통해 사용자는 기초자산의 가격이 최초기준가격 대비 몇 퍼센트 상승하거나 하락했는지를 파악하고, 낙인 조건 도달 여부를 확인할 수 있습니다.<br/><br/>
                            **recentAndInitialPriceRatio**: 각 기초자산들의 최초기준가격 대비 현재 기초자산가격 비율들 중에 가장 낮은 비율
                        """,
            response_model=PriceRatioResponse,
            responses={
                **product_service_exception_response,
                **validate_initial_price_exception_response
            })
async def get_price_ratio(request: Request, productId: int = Path(..., description="조회할 상품 id")):
    requestId = request.headers.get("requestId")

    # 특정 상품 단건 조회 API 통신
    try:
        headers = {"requestId": requestId}
        responseProduct = await eureka_client.do_service_async("product-service", f"/v1/product/{productId}", headers=headers)
        product = json.loads(responseProduct)
    except urllib.error.URLError as e:
        raise ProductServiceServerException(productId)

    # product-service로 부터 받은 값 변수 초기화
    initialBasePriceEvaluationDate = product["initialBasePriceEvaluationDate"]
    equities = product["equities"].split(" / ")
    equityTickerSymbols = product["equityTickerSymbols"]

    if datetime.strptime(initialBasePriceEvaluationDate, "%Y-%m-%d").date() > datetime.now().date():
        raise ValidateInitialBasePriceEvaluationDateException(productId)

    # yfinance에 최초기준가격평가일에 대한 각 기초자산들의 종가 데이터들 가져오기
    result = {}
    initial_tmp = {}
    for equity in equities:
        stock_data = yf.Ticker(equityTickerSymbols[equity])
        initial_data = stock_data.history(start=initialBasePriceEvaluationDate,
                                          end=pd.Timestamp(initialBasePriceEvaluationDate) + pd.Timedelta(days=1))

        try:
            initial_close_price = initial_data.loc[initialBasePriceEvaluationDate, "Close"]
        except:
            raise ValidateInitialBasePriceEvaluationDateException(productId)

        initial_tmp[equity] = initial_close_price
    result["initial"] = initial_tmp

    # yfinace에 오늘 날짜에 대한 각 기초자산들의 종가 데이터 가져오기 (현재 기초자산이 속한 장이 열려 있다면 실시간 값을 가져오게 됨)
    recent_tmp = {}
    for equity in equities:
        stock_data = yf.Ticker(equityTickerSymbols[equity])
        recent_data = stock_data.history(period="1d")

        recent_close_price = recent_data['Close'].iloc[-1]
        recent_tmp[equity] = recent_close_price
    result["recent"] = recent_tmp

    # 최초기준가격 대비 최근 기초자산가격
    minComparedValue = float('inf')
    ratio_tmp = {}
    for equity in equities:
        x = result["initial"][equity]
        y = result["recent"][equity]
        ratio_tmp[equity] = round((y / x) * 100, 2)
        minComparedValue = min(minComparedValue, round((y / x) * 100, 2))
    result["ratio"] = ratio_tmp
    result["recentAndInitialPriceRatio"] = round((minComparedValue - 100), 2)

    return result

@router.post("/price/ratio/list",
            summary="여러 상품 id에 대한 최초기준가격 대비 현재 기초자산가격 비율 리스트 조회",
            description="""
                            **recentAndInitialPriceRatio**: 각 기초자산들의 최초기준가격 대비 현재 기초자산가격 비율들 중에 가장 낮은 비율(종가 데이터를 못 가져오는 경우 null 값 반환)
                        """,
            response_model=List[PriceRatio],
            responses={
                **product_service_exception_response,
                **validate_initial_price_exception_response
            })
async def get_price_ratio_list(request: Request, data: ProductIdListModel):
    productIdList = data.productIdList
    requestId = request.headers.get("requestId")

    async def fetch_product_info(productId):
        try:
            headers = {"requestId": requestId}
            responseProduct = await eureka_client.do_service_async("product-service", f"/v1/product/{productId}", headers=headers)
            return json.loads(responseProduct)
        except urllib.error.URLError as e:
            raise ProductServiceServerException(productId)

    async def fetch_initial_prices(stock_data, initialBasePriceEvaluationDate):
        return stock_data.history(start=initialBasePriceEvaluationDate,
                                  end=pd.Timestamp(initialBasePriceEvaluationDate) + pd.Timedelta(days=1))

    async def fetch_recent_prices(stock_data):
        return stock_data.history(period="1d")

    result = []

    productResults = await asyncio.gather(*[fetch_product_info(productId) for productId in productIdList])

    for productResult in productResults:
        tmp = {}
        productId = productResult["id"]
        initialBasePriceEvaluationDate = productResult["initialBasePriceEvaluationDate"]
        equities = productResult["equities"].split(" / ")
        equityTickerSymbols = productResult["equityTickerSymbols"]

        tmp["id"] = productId

        if datetime.strptime(initialBasePriceEvaluationDate, "%Y-%m-%d").date() > datetime.now().date():
            tmp["recentAndInitialPriceRatio"] = None
            result.append(tmp)
            continue

        # 각각의 종목에 대해 초기 및 최근 가격을 비동기적으로 가져옴
        tasks = []
        for equity in equities:
            stock_data = yf.Ticker(equityTickerSymbols[equity])
            tasks.append(asyncio.gather(
                fetch_initial_prices(stock_data, initialBasePriceEvaluationDate),
                fetch_recent_prices(stock_data)
            ))

        price_data = await asyncio.gather(*tasks)

        # 최초기준가격 대비 최근 기초자산가격
        minComparedValue = float('inf')
        initialBasePriceEvaluationDateFlag = False
        for (initial_data, recent_data), equity in zip(price_data, equities):
            try:
                initial_close_price = initial_data.loc[initialBasePriceEvaluationDate, "Close"]
            except:
                tmp["recentAndInitialPriceRatio"] = None
                initialBasePriceEvaluationDateFlag = True
                break

            recent_close_price = recent_data['Close'].iloc[-1]
            minComparedValue = min(minComparedValue, round((recent_close_price / initial_close_price) * 100, 2))

        if not initialBasePriceEvaluationDateFlag:
            tmp["recentAndInitialPriceRatio"] = round((minComparedValue - 100), 2)

        result.append(tmp)

    return result

