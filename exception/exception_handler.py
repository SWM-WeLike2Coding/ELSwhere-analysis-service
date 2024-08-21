import uuid
from datetime import datetime
from urllib.request import Request
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from exception.errors import ProductServiceServerException

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