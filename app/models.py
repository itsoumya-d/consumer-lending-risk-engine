from enum import Enum
from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REFERRED = "REFERRED"
    DECLINED = "DECLINED"


class RiskTier(str, Enum):
    TIER_A = "TIER_A"
    TIER_B = "TIER_B"
    TIER_C = "TIER_C"
    UNASSIGNED = "UNASSIGNED"


class UnderwritingRequest(BaseModel):
    applicant_id: str = Field(..., description="Unique applicant identifier", min_length=3)
    age: int = Field(..., ge=0, le=120, description="Applicant age in years")
    annual_income: float = Field(..., ge=0.0, description="Gross annual income in GBP")
    monthly_debt_obligations: float = Field(..., ge=0.0, description="Existing monthly debt servicing commitments")
    credit_score: int = Field(..., ge=300, le=850, description="Bureau credit risk score (300-850)")
    requested_amount: float = Field(..., gt=0.0, description="Requested borrowing or credit line amount")
    has_bankruptcies: bool = Field(default=False, description="Whether applicant has recorded bankruptcies")
    has_recent_ccj: bool = Field(default=False, description="Whether applicant has unsatisfied County Court Judgments")


class UnderwritingDecision(BaseModel):
    applicant_id: str
    status: DecisionStatus
    risk_tier: RiskTier
    approved_limit: float
    offered_apr: float | None = None
    debt_to_income_ratio: float
    monthly_disposable_income: float
    decision_reasons: list[str]


class HealthResponse(BaseModel):
    status: str
    version: str
