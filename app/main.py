from fastapi import FastAPI, status
from app import __version__
from app.engine import UnderwritingEngine
from app.models import HealthResponse, UnderwritingDecision, UnderwritingRequest

app = FastAPI(
    title="Consumer Lending Risk & Underwriting Engine",
    description="Deterministic credit decisioning and risk assessment API",
    version=__version__,
)

engine = UnderwritingEngine()


@app.get("/v1/health", response_model=HealthResponse, tags=["Monitoring"])
def get_health() -> HealthResponse:
    return HealthResponse(status="healthy", version=__version__)


@app.post("/v1/underwrite/assess", response_model=UnderwritingDecision, status_code=status.HTTP_200_OK, tags=["Underwriting"])
def assess_applicant(request: UnderwritingRequest) -> UnderwritingDecision:
    return engine.evaluate(request)
