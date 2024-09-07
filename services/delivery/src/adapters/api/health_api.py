from fastapi import APIRouter, Depends
from src.adapters.dependencies import get_health_service
from src.application.dto.health_dto import HealthResponse
from src.infrastructure.health.health_service import HealthService

router = APIRouter()


@router.get("/health", tags=["Health"], response_model=HealthResponse)
def health_check(health_service: HealthService = Depends(get_health_service)):
    return health_service.get_health_status()
