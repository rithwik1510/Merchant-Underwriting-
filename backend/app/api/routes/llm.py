from fastapi import APIRouter

from app.schemas import LLMProbeRequest, LLMProbeResponse, LLMSettingsResponse, LLMSettingsUpdateRequest
from app.services.llm_probe_service import probe_llm_provider
from app.services.llm_settings_service import get_llm_settings, update_llm_settings


router = APIRouter()


@router.post("/probe", response_model=LLMProbeResponse)
def probe_provider(request: LLMProbeRequest) -> LLMProbeResponse:
    return probe_llm_provider(request)


@router.get("/settings", response_model=LLMSettingsResponse)
def read_settings() -> LLMSettingsResponse:
    return get_llm_settings()


@router.put("/settings", response_model=LLMSettingsResponse)
def write_settings(request: LLMSettingsUpdateRequest) -> LLMSettingsResponse:
    return update_llm_settings(request)
