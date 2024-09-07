from unittest.mock import MagicMock

import pytest
from src.adapters.api.health_api import health_check
from src.infrastructure.health.health_service import HealthService


@pytest.fixture
def mock_health_service():
    return MagicMock(spec=HealthService)


def test_health_check(mock_health_service):
    mock_health_service.get_health_status.return_value = {"status": "ok"}

    result = health_check(health_service=mock_health_service)

    assert result == {"status": "ok"}
    mock_health_service.get_health_status.assert_called_once()
