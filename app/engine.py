from app.models import DecisionStatus, RiskTier, UnderwritingDecision, UnderwritingRequest

BASELINE_LIVING_COST_GBP = 750.0


class UnderwritingEngine:
    """Core deterministic risk assessment and underwriting policy engine."""

    def __init__(self, baseline_living_cost: float = BASELINE_LIVING_COST_GBP):
        self.baseline_living_cost = baseline_living_cost

    def evaluate(self, request: UnderwritingRequest) -> UnderwritingDecision:
        reasons: list[str] = []

        # 1. Hard Exclusion Criteria
        if request.age < 18:
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.DECLINED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=0.0,
                monthly_disposable_income=0.0,
                decision_reasons=["Applicant under legal age limit (18)."],
            )

        if request.has_bankruptcies:
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.DECLINED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=0.0,
                monthly_disposable_income=0.0,
                decision_reasons=["Active bankruptcy record detected."],
            )

        if request.has_recent_ccj:
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.DECLINED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=0.0,
                monthly_disposable_income=0.0,
                decision_reasons=["Unsatisfied County Court Judgment (CCJ) detected."],
            )

        # 2. Income & Affordability Calculations
        monthly_gross = request.annual_income / 12.0
        if monthly_gross <= 0:
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.DECLINED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=1.0,
                monthly_disposable_income=0.0,
                decision_reasons=["Zero or negative declared gross income."],
            )

        dti = round(request.monthly_debt_obligations / monthly_gross, 4)
        monthly_disposable = round(monthly_gross - request.monthly_debt_obligations - self.baseline_living_cost, 2)

        if monthly_disposable <= 0:
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.DECLINED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=dti,
                monthly_disposable_income=monthly_disposable,
                decision_reasons=["Failed affordability check: negative net disposable income after baseline living costs."],
            )

        # 3. Credit Scoring & Risk Tiering
        score = request.credit_score

        if score >= 740 and dti <= 0.35:
            risk_tier = RiskTier.TIER_A
            apr = 14.9
            max_borrowing_cap = 15000.0
            borrowing_capacity = monthly_disposable * 12.0
            approved_limit = min(request.requested_amount, borrowing_capacity, max_borrowing_cap)
            reasons.append("Prime credit profile with strong debt service coverage.")
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.APPROVED,
                risk_tier=risk_tier,
                approved_limit=round(approved_limit, 2),
                offered_apr=apr,
                debt_to_income_ratio=dti,
                monthly_disposable_income=monthly_disposable,
                decision_reasons=reasons,
            )

        elif score >= 660 and dti <= 0.45:
            risk_tier = RiskTier.TIER_B
            apr = 22.9
            max_borrowing_cap = 8000.0
            borrowing_capacity = monthly_disposable * 8.0
            approved_limit = min(request.requested_amount, borrowing_capacity, max_borrowing_cap)
            reasons.append("Near-prime credit profile meeting standard risk criteria.")
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.APPROVED,
                risk_tier=risk_tier,
                approved_limit=round(approved_limit, 2),
                offered_apr=apr,
                debt_to_income_ratio=dti,
                monthly_disposable_income=monthly_disposable,
                decision_reasons=reasons,
            )

        elif score >= 580 and dti <= 0.50:
            risk_tier = RiskTier.TIER_C
            apr = 34.9
            max_borrowing_cap = 3000.0
            borrowing_capacity = monthly_disposable * 4.0
            approved_limit = min(request.requested_amount, borrowing_capacity, max_borrowing_cap)
            reasons.append("Emerging credit profile with capped risk exposure.")
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.APPROVED,
                risk_tier=risk_tier,
                approved_limit=round(approved_limit, 2),
                offered_apr=apr,
                debt_to_income_ratio=dti,
                monthly_disposable_income=monthly_disposable,
                decision_reasons=reasons,
            )

        # 4. Borderline / Referral Evaluation
        elif (score >= 550 and dti <= 0.55) or (score >= 680 and dti <= 0.52):
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.REFERRED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=dti,
                monthly_disposable_income=monthly_disposable,
                decision_reasons=["Borderline score or elevated DTI; referred for manual underwriter review."],
            )

        # 5. Out of Risk Appetite Decline
        else:
            return UnderwritingDecision(
                applicant_id=request.applicant_id,
                status=DecisionStatus.DECLINED,
                risk_tier=RiskTier.UNASSIGNED,
                approved_limit=0.0,
                offered_apr=None,
                debt_to_income_ratio=dti,
                monthly_disposable_income=monthly_disposable,
                decision_reasons=[f"Risk score ({score}) or debt-to-income ratio ({dti}) outside automated risk appetite."],
            )
