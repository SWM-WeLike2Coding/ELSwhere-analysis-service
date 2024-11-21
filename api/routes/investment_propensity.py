from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field, field_validator
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from dependencies import get_db
from util.repayment_option import RepaymentOption
from util.risk_propensity import RiskPropensity
from sqlalchemy.future import select
from models import AIResult, MonteCarloResult
import os

router = APIRouter()

class RequestInvestmentPropensityInformation(BaseModel):
    productIdList: List[int]
    riskPropensity: str = Field("EXTREME_RISK")
    repaymentOption: str = Field("EARLY_REPAYMENT")

    @field_validator('riskPropensity')
    def validate_risk_propensity(cls, v):
        try:
            return RiskPropensity[v]
        except KeyError:
            raise ValueError(f"유효하지 않은 riskPropensity 값입니다: {v}")

    @field_validator('repaymentOption')
    def validate_repayment_option(cls, v):
        try:
            return RepaymentOption[v]
        except KeyError:
            raise ValueError(f"유효하지 않은 repaymentOption 값입니다: {v}")

class ResponseProductIdList(BaseModel):
    productIdList: List[int]

@router.post("/list",
             summary="투자 성향에 만족하는 상품 id 리스트",
             description="riskTakingAbility(투자자 위험 감수 능력) : EXTREME_RISK(초고위험), HIGH_RISK(고위험), MEDIUM_RISK(중위험), LOW_RISK(저위험)<br/> \
                            repaymentOption(희망 상환 기간) : EARLY_REPAYMENT(조기상환), MATURITY_REPAYMENT(만기상환), NO_PREFERENCE(상관없음)",
             response_model=List[int])
async def get_satisfied_investment_propensity_products(request: RequestInvestmentPropensityInformation = Body(..., description="투자 성향을 확인할 정보"),
                                                       db: AsyncSession = Depends(get_db)):
    async with db as session:
        riskPropensityQueryResult = await session.execute(get_product_ids_by_risk_propensity(
                                                    request.productIdList,
                                                    request.riskPropensity)
                                                )
        satisfiedRiskPropensityProductIdList = riskPropensityQueryResult.scalars().all()

        if not satisfiedRiskPropensityProductIdList:
            return []

        if request.repaymentOption == RepaymentOption.NO_PREFERENCE:
            return satisfiedRiskPropensityProductIdList

        investmentPropensityQueryResult = await session.execute(get_product_ids_by_repayment_option(request.satisfiedRiskPropensityProductIdList,
                                                                                                    request.repaymentOption))
        satisfiedInvestmentPropensityProductIdList = investmentPropensityQueryResult.scalars().all()

        return satisfiedInvestmentPropensityProductIdList


def get_product_ids_by_risk_propensity(productIdList, risk_propensity):
    if risk_propensity == RiskPropensity.LOW_RISK:
        min_score = float(os.getenv('MEDIUM_AND_LOW_RISK_BOUNDARY'))
        max_score = 1
    elif risk_propensity == RiskPropensity.MEDIUM_RISK:
        min_score = float(os.getenv('HIGH_AND_MEDIUM_RISK_BOUNDARY'))
        max_score = float(os.getenv('MEDIUM_AND_LOW_RISK_BOUNDARY'))
    elif risk_propensity == RiskPropensity.HIGH_RISK:
        min_score = float(os.getenv('EXTREME_AND_HIGH_RISK_BOUNDARY'))
        max_score = float(os.getenv('HIGH_AND_MEDIUM_RISK_BOUNDARY'))
    elif risk_propensity == RiskPropensity.EXTREME_RISK:
        min_score = 0
        max_score = float(os.getenv('EXTREME_AND_HIGH_RISK_BOUNDARY'))
    else:
        return []

    # 쿼리 작성
    query = (
        select(AIResult.product_id)
        .where(
            AIResult.product_id.in_(productIdList),
            AIResult.safety_score >= min_score,
            AIResult.safety_score < max_score
        )
    )

    return query

def get_product_ids_by_repayment_option(productIdList, repayment_option):
    if repayment_option == RepaymentOption.EARLY_REPAYMENT:
        boundary_value = int(os.getenv('EARLY_REPAYMENT_BOUNDARY'))
        query = (
            select(MonteCarloResult.product_id)
            .where(
                MonteCarloResult.product_id.in_(productIdList),
                text(
                    "CAST(SUBSTRING_INDEX(early_repayment_probability, ',', 1) AS DECIMAL(8, 4)) + "
                    "CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(early_repayment_probability, ',', 2), ',', -1) AS DECIMAL(8, 4)) >= :boundary"
                ).bindparams(boundary=boundary_value)
            )
        )

    elif repayment_option == RepaymentOption.MATURITY_REPAYMENT:
        query = (
            select(MonteCarloResult.product_id)
            .where(
                MonteCarloResult.product_id.in_(productIdList),
                MonteCarloResult.loss_probability <= int(os.getenv('MATURITY_REPAYMENT_BOUNDARY'))
            )
        )

    return query