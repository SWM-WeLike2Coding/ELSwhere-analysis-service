from fastapi import APIRouter, Path, Depends, Body
from pydantic import BaseModel
from typing import List
from exception.errors import AIResultException
from exception.error_response_examples import ai_result_exception_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import AIResult
from dependencies import get_db

router = APIRouter()


class ProductIdListModel(BaseModel):
    productIdList: List[int]

class AISingleResponse(BaseModel):
    AIResultId: int
    productId: int
    repaymentPrediction: bool
    safetyScore: float

class AIResponse(BaseModel):
    AIResultId: int
    productId: int
    safetyScore: float

@router.get("/{productId}",
            summary="상품 단건에 대한 AI 분석 결과 조회",
            response_model=AISingleResponse,
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

        return AISingleResponse(
            AIResultId=ai_result.ai_result_id,
            productId=ai_result.product_id,
            repaymentPrediction=ai_result.repayment_prediction,
            safetyScore=ai_result.safety_score
        )


@router.post("/list",
             summary="여러 상품 id에 대한 AI 분석 결과 리스트 조회",
             response_model=List[AIResponse])
async def get_ai_list(request: ProductIdListModel = Body(..., description="조회할 상품 ID 리스트"),
                       db: AsyncSession = Depends(get_db)):
    async with db as session:
        results = await session.execute(
            select(AIResult).where(AIResult.product_id.in_(request.productIdList))
        )
        ai_results = results.scalars().all()

        # 조회된 AI 결과를 AIResponse 형식으로 변환
        response_list = [
            AIResponse(
                AIResultId=result.ai_result_id,
                productId=result.product_id,
                safetyScore=result.safety_score
            )
            for result in ai_results
        ]

        return response_list
