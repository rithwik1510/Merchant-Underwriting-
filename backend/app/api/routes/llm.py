from fastapi import APIRouter

from app.schemas import LLMProbeRequest, LLMProbeResponse
from app.services.llm_probe_service import probe_llm_provider


router = APIRouter()


@router.post("/probe", response_model=LLMProbeResponse)
def probe_provider(request: LLMProbeRequest) -> LLMProbeResponse:
    return probe_llm_provider(request)
