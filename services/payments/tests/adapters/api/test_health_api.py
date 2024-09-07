from unittest.mock import MagicMock, patch

import pytest
from src.adapters.api.health_api import health_check
from src.infrastructure.health.health_service import HealthService


@patch("src.adapters.api.health_api.get_health_service")
def test_health_check(mock_get_health_service):
    # Create a mock HealthService instance
    mock_health_service = MagicMock(spec=HealthService)

    # Define the expected health status return value
    expected_health_status = {
        "mongodb": "healthy",
        "rabbitmq": "healthy",
    }

    # Set up the mock to return the expected health status
    mock_health_service.get_health_status.return_value = expected_health_status
    mock_get_health_service.return_value = mock_health_service

    # Call the health_check function
    response = health_check(health_service=mock_health_service)

    # Assert that the get_health_status method was called once
    mock_health_service.get_health_status.assert_called_once()

    # Assert that the response is as expected
    assert response == expected_health_status
