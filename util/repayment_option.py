from enum import Enum

class RepaymentOption(Enum):
    EARLY_REPAYMENT = "조기상환"
    MATURITY_REPAYMENT = "만기상환"
    NO_PREFERENCE = "상관없음"

    def __str__(self):
        return self.name