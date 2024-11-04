from enum import Enum

class RiskPropensity(Enum):
    EXTREME_RISK = "초고위험"
    HIGH_RISK = "고위험"
    MEDIUM_RISK = "중위험"
    LOW_RISK = "저위험"

    def __str__(self):
        return self.name