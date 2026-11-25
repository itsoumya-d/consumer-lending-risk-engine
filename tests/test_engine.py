import pytest
from app.engine import UnderwritingEngine
from app.models import DecisionStatus, RiskTier, UnderwritingRequest


@pytest.fixture
def engine():
    return UnderwritingEngine(baseline_living_cost=750.0)


def test_hard_exclusion_underage(engine):
    req = UnderwritingRequest(
        applicant_id="app-underage-01",
        age=17,
        annual_income=45000.0,
        monthly_debt_obligations=200.0,
        credit_score=750,
        requested_amount=2500.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.DECLINED
    assert "under legal age limit" in decision.decision_reasons[0].lower()
    assert decision.approved_limit == 0.0


def test_hard_exclusion_bankruptcy(engine):
    req = UnderwritingRequest(
        applicant_id="app-bankrupt-01",
        age=32,
        annual_income=55000.0,
        monthly_debt_obligations=150.0,
        credit_score=720,
        requested_amount=5000.0,
        has_bankruptcies=True,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.DECLINED
    assert "bankruptcy" in decision.decision_reasons[0].lower()


def test_hard_exclusion_ccj(engine):
    req = UnderwritingRequest(
        applicant_id="app-ccj-01",
        age=28,
        annual_income=50000.0,
        monthly_debt_obligations=100.0,
        credit_score=700,
        requested_amount=3000.0,
        has_recent_ccj=True,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.DECLINED
    assert "ccj" in decision.decision_reasons[0].lower()


def test_affordability_failure(engine):
    # Monthly gross = £1500, Debt = £900, Baseline Living = £750 -> Disposable = -£150
    req = UnderwritingRequest(
        applicant_id="app-poor-affordability",
        age=30,
        annual_income=18000.0,
        monthly_debt_obligations=900.0,
        credit_score=700,
        requested_amount=2000.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.DECLINED
    assert "affordability" in decision.decision_reasons[0].lower()
    assert decision.monthly_disposable_income < 0


def test_tier_a_approval(engine):
    # High score (780), low DTI, ample disposable income
    req = UnderwritingRequest(
        applicant_id="app-tier-a",
        age=35,
        annual_income=84000.0,  # 7000/mo
        monthly_debt_obligations=500.0,  # DTI = 500/7000 = 0.071
        credit_score=780,
        requested_amount=10000.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.APPROVED
    assert decision.risk_tier == RiskTier.TIER_A
    assert decision.offered_apr == 14.9
    assert decision.approved_limit == 10000.0


def test_tier_b_approval(engine):
    req = UnderwritingRequest(
        applicant_id="app-tier-b",
        age=29,
        annual_income=48000.0,  # 4000/mo
        monthly_debt_obligations=1200.0,  # DTI = 0.30
        credit_score=680,
        requested_amount=6000.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.APPROVED
    assert decision.risk_tier == RiskTier.TIER_B
    assert decision.offered_apr == 22.9
    assert decision.approved_limit == 6000.0


def test_tier_c_approval(engine):
    req = UnderwritingRequest(
        applicant_id="app-tier-c",
        age=24,
        annual_income=30000.0,  # 2500/mo
        monthly_debt_obligations=1000.0,  # DTI = 0.40
        credit_score=610,
        requested_amount=2500.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.APPROVED
    assert decision.risk_tier == RiskTier.TIER_C
    assert decision.offered_apr == 34.9
    assert decision.approved_limit == 2500.0


def test_borderline_referral(engine):
    req = UnderwritingRequest(
        applicant_id="app-referral",
        age=42,
        annual_income=36000.0,  # 3000/mo
        monthly_debt_obligations=1600.0,  # DTI = 0.533
        credit_score=560,
        requested_amount=1500.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.REFERRED
    assert decision.approved_limit == 0.0
    assert "manual underwriter review" in decision.decision_reasons[0].lower()


def test_subprime_decline(engine):
    req = UnderwritingRequest(
        applicant_id="app-subprime",
        age=38,
        annual_income=30000.0,
        monthly_debt_obligations=1600.0,
        credit_score=480,
        requested_amount=2000.0,
    )
    decision = engine.evaluate(req)
    assert decision.status == DecisionStatus.DECLINED
    assert "outside automated risk appetite" in decision.decision_reasons[0].lower()
