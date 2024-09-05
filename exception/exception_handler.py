import uuid
from datetime import datetime
from urllib.request import Request
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from exception.errors import ProductServiceServerException, ValidateInitialBasePriceEvaluationDateException

def add_exception_handler(app: FastAPI):
    @app.exception_handler(ProductServiceServerException)
    async def product_service_server_exception_handler(request: Request, exc: ProductServiceServerException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": str(datetime.now()),
                "trackingId": str(uuid.uuid4()),
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status": "INTERNAL_SERVER_ERROR",
                "code": "ProductServiceServerException",
                "message": "상품 서비스와 통신 중 문제가 발생하였습니다."
            }
        )

    @app.exception_handler(ValidateInitialBasePriceEvaluationDateException)
    async def validate_initial_base_price_evaluation_date_exception_handler(request: Request,
                                                                            exc: ValidateInitialBasePriceEvaluationDateException):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "timestamp": str(datetime.now()),
                "trackingId": str(uuid.uuid4()),
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "status": "UNPROCESSABLE_ENTITY",
                "code": "ValidateInitialBasePriceEvaluationDateException",
                "message": "최초기준가격평가일이 계산하고자 하는 현재 시점 보다 미래의 날짜이므로 종가 데이터를 가져올 수 없습니다."
            }
        )