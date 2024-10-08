from sqlalchemy.sql import func
from core.database import Base
from sqlalchemy import Column, BigInteger, DECIMAL, Text, DateTime


class MonteCarloResult(Base):
    __tablename__ = 'monte_carlo_result'

    monte_carlo_result_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    product_id = Column(BigInteger, nullable=False)
    early_repayment_probability = Column(Text, nullable=False)
    maturity_repayment_probability = Column(DECIMAL(8,4), nullable=False)
    loss_probability = Column(DECIMAL(8,4), nullable=False)
    under_knockin_barrier_probability = Column(DECIMAL(8,4), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class MonteCarloResultError(Base):
    __tablename__ = 'monte_carlo_result_error'

    monte_carlo_result_error_id = Column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    product_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)