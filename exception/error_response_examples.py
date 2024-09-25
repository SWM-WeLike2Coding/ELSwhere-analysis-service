import uuid
from datetime import datetime

product_service_exception_response = {
    500: {
        "description": "상품 서비스와 통신 중 문제가 발생하였습니다.",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": str(datetime.now()),
                    "trackingId": str(uuid.uuid4()),
                    "status_code": 500,
                    "status": "INTERNAL_SERVER_ERROR",
                    "code": "ProductServiceServerException",
                    "message": "상품 서비스와 통신 중 문제가 발생하였습니다."
                }
            }
        }
    }
}

validate_initial_price_exception_response = {
    422: {
        "description": "최초기준가격평가일이 계산하고자 하는 현재 시점 보다 미래의 날짜이므로 종가 데이터를 가져올 수 없습니다.",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": str(datetime.now()),
                    "trackingId": str(uuid.uuid4()),
                    "status_code": 422,
                    "status": "UNPROCESSABLE_ENTITY",
                    "code": "ValidateInitialBasePriceEvaluationDateException",
                    "message": "최초기준가격평가일이 계산하고자 하는 현재 시점 보다 미래의 날짜이므로 종가 데이터를 가져올 수 없습니다."
                }
            }
        }
    }
}

monte_carlo_result_exception_response = {
    404: {
        "description": "해당 상품에 대한 몬테카를로 분석 결과를 찾을 수 없습니다.",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": str(datetime.now()),
                    "trackingId": str(uuid.uuid4()),
                    "status_code": 404,
                    "status": "NOT_FOUND",
                    "code": "MonteCarloResultException",
                    "message": "해당 상품에 대한 몬테카를로 분석 결과를 찾을 수 없습니다."
                }
            }
        }
    }
}
