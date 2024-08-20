from fastapi import APIRouter, HTTPException, Path
from typing import Dict
from pydantic import BaseModel, RootModel
import py_eureka_client.eureka_client as eureka_client
import pandas as pd
import json
import urllib.request
import yfinance as yf

router = APIRouter()

class PriceData(RootModel[Dict[str, float]]):
    pass
class PriceRatioResponse(BaseModel):
    initial: PriceData
    recent: PriceData
    ratio: PriceData
    recentAndInitialPriceRatio: float

@router.get("/price/ratio/{productId}",
            summary="최초기준가격 대비 현재 기초자산가격 비율",
            description="""
                            각 상품에 존재하는 기초자산들의 최초기준가격 대비 현재 기초자산가격 비율 정보들을 제공합니다.<br/>
                            이 비율 정보들을 통해 사용자는 기초자산의 가격이 최초기준가격 대비 몇 퍼센트 상승하거나 하락했는지를 파악하고, 낙인 조건 도달 여부를 확인할 수 있습니다.<br/><br/>
                            **recentAndInitialPriceRatio**: 각 기초자산들의 최초기준가격 대비 현재 기초자산가격 비율들 중에 가장 낮은 비율
                        """,
            response_model=PriceRatioResponse
            )
async def get_price_ratio(productId: int = Path(..., description="조회할 상품 id")):
    # 특정 상품 단건 조회 API 통신
    try:
        responseProduct = await eureka_client.do_service_async("product-service", f"/v1/product/{productId}")
        product = json.loads(responseProduct)
    except urllib.request.HTTPError as e:
        raise HTTPException(status_code=e.code, detail=str(e))

    # product-service로 부터 받은 값 변수 초기화
    initialBasePriceEvaluationDate = product["initialBasePriceEvaluationDate"]
    equities = product["equities"].split(" / ")
    equityTickerSymbols = product["equityTickerSymbols"]

    # yfinance에 최초기준가격평가일에 대한 각 기초자산들의 종가 데이터들 가져오기
    result = {}
    initial_tmp = {}
    for equity in equities:
        stock_data = yf.Ticker(equityTickerSymbols[equity])
        initial_data = stock_data.history(start=initialBasePriceEvaluationDate,
                                          end=pd.Timestamp(initialBasePriceEvaluationDate) + pd.Timedelta(days=1))

        initial_close_price = initial_data.loc[initialBasePriceEvaluationDate, "Close"]
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
    minComparedValue = 0x7fffffff
    ratio_tmp = {}
    for equity in equities:
        x = result["initial"][equity]
        y = result["recent"][equity]
        ratio_tmp[equity] = round((y / x) * 100, 2)
        minComparedValue = min(minComparedValue, round((y / x) * 100, 2))
    result["ratio"] = ratio_tmp
    result["recentAndInitialPriceRatio"] = round((minComparedValue - 100), 2)

    return result

