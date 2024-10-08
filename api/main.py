from fastapi import APIRouter
from api.routes import product, monte_carlo

api_router = APIRouter()
api_router.include_router(product.router, prefix="/v1/product", tags=["상품 분석"])
api_router.include_router(monte_carlo.router, prefix="/v1/monte-carlo", tags=["몬테카를로 분석"])