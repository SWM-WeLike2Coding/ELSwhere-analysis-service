from fastapi import APIRouter, Path, Depends
from pydantic import BaseModel
from exception.errors import MonteCarloResultException
from exception.error_response_examples import monte_carlo_result_exception_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import MonteCarloResult
from dependencies import get_db

router = APIRouter()

class MonteCarloResponse(BaseModel):
    monteCarloResultId: int
    productId: int
    earlyRepaymentProbability: str
    maturityRepaymentProbability: float
    lossProbability: float
    underKnockInBarrierProbability: float

@router.get("/{productId}",
            summary="상품 단건에 대한 몬테카를로 분석 결과 조회",
            response_model=MonteCarloResponse,
            responses={
                **monte_carlo_result_exception_response
            })
async def get_monte_carlo(productId: int = Path(..., description="조회할 상품 id"),
                          db: AsyncSession = Depends(get_db)):
    async with db as session:
        result = await session.execute(select(MonteCarloResult).where(MonteCarloResult.product_id == productId))
        monte_carlo_result = await result.scalars().first()

        if monte_carlo_result is None:
            raise MonteCarloResultException(productId)

        return MonteCarloResponse(
            monteCarloResultId=monte_carlo_result.monte_carlo_result_id,
            productId=monte_carlo_result.product_id,
            earlyRepaymentProbability=monte_carlo_result.early_repayment_probability,
            maturityRepaymentProbability=monte_carlo_result.maturity_repayment_probability,
            lossProbability=monte_carlo_result.loss_probability,
            underKnockInBarrierProbability=monte_carlo_result.under_knockin_barrier_probability
        )