import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.services.order_verification_service import (
    OrderVerificationService,
)
from src.config import Config


class TestOrderVerificationService(unittest.TestCase):
    def setUp(self):
        self.order_verification_service = OrderVerificationService()
        self.valid_order_id = 123
        self.invalid_order_id = 999

    @patch.object(Config, "ORDER_SERVICE_BASE_URL", "http://test-url")
    @patch("aiohttp.ClientSession")
    def test_verify_order_success(self, mock_client_session):
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "confirmed"})
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_client_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = asyncio.run(
            self.order_verification_service.verify_order(self.valid_order_id)
        )

        # Assert
        self.assertTrue(result)
        get = mock_client_session.return_value.__aenter__.return_value.get
        get.assert_called_once_with(f"http://test-url/{self.valid_order_id}")

    @patch.object(Config, "ORDER_SERVICE_BASE_URL", "http://test-url")
    @patch("aiohttp.ClientSession")
    def test_verify_order_canceled(self, mock_client_session):
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"status": "canceled"})
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_client_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = asyncio.run(
            self.order_verification_service.verify_order(self.valid_order_id)
        )

        # Assert
        self.assertFalse(result)
        get = mock_client_session.return_value.__aenter__.return_value.get
        get.assert_called_once_with(f"http://test-url/{self.valid_order_id}")

    @patch.object(Config, "ORDER_SERVICE_BASE_URL", "http://test-url")
    @patch("aiohttp.ClientSession")
    def test_verify_order_not_found(self, mock_client_session):
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_client_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = asyncio.run(
            self.order_verification_service.verify_order(self.invalid_order_id)
        )

        # Assert
        self.assertFalse(result)
        get = mock_client_session.return_value.__aenter__.return_value.get
        get.assert_called_once_with(f"http://test-url/{self.invalid_order_id}")

    @patch.object(Config, "ORDER_SERVICE_BASE_URL", "http://test-url")
    @patch("aiohttp.ClientSession")
    def test_verify_order_exception(self, mock_client_session):
        # Arrange
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.side_effect = Exception(
            "Some error"
        )
        mock_client_session.return_value.__aenter__.return_value = mock_session

        # Act
        result = asyncio.run(
            self.order_verification_service.verify_order(self.valid_order_id)
        )

        # Assert
        self.assertFalse(result)
        get = mock_client_session.return_value.__aenter__.return_value.get
        get.assert_called_once_with(f"http://test-url/{self.valid_order_id}")


if __name__ == "__main__":
    unittest.main()
