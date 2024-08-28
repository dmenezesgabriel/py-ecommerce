from unittest.mock import MagicMock, patch

import pytest
from src.adapters.api.health_api import health_check


class TestHealthAPI:

    @patch("src.adapters.api.health_api.get_health_service")
    def test_health_check(self, mock_get_health_service):
        # Arrange
        mock_service = MagicMock()
        mock_health_status = {"status": "ok"}
        mock_service.get_health_status.return_value = mock_health_status
        mock_get_health_service.return_value = mock_service

        # Act
        response = health_check(service=mock_service)

        # Assert
        mock_service.get_health_status.assert_called_once()
        assert response == mock_health_status


if __name__ == "__main__":
    pytest.main()
