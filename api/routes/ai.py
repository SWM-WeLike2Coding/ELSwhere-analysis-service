from fastapi import APIRouter, Path, Depends
from pydantic import BaseModel
from exception.errors import AIResultException
from exception.error_response_examples import ai_result_exception_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import AIResult
from dependencies import get_db

router = APIRouter()

class AIResponse(BaseModel):
    AIResultId: int
    productId: int
    repaymentPrediction: bool
    accuracy: float

@router.get("/{productId}",
            summary="상품 단건에 대한 AI 분석 결과 조회",
            response_model=AIResponse,
            responses={
                **ai_result_exception_response
            })
async def get_ai(productId: int = Path(..., description="조회할 상품 id"),
                          db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(AIResult).where(AIResult.product_id == productId))
        ai_result = result.scalars().first()

        if ai_result is None:
            raise AIResultException(productId)

        return AIResponse(
            AIResultId=ai_result.ai_result_id,
            productId=ai_result.product_id,
            repaymentPrediction=ai_result.repayment_prediction,
            accuracy=ai_result.accuracy
        )