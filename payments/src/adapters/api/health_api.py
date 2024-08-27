from fastapi import APIRouter, Depends
from src.adapters.dependencies import get_health_service
from src.infrastructure.health.health_service import HealthService

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check(health_service: HealthService = Depends(get_health_service)):
    return health_service.get_health_status()
