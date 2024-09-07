import unittest
from unittest.mock import MagicMock, patch

from fastapi import FastAPI


class TestMainApp(unittest.TestCase):
    @patch("src.adapters.api.customer_api.router")
    @patch("src.adapters.api.delivery_api.router")
    @patch("src.adapters.api.health_api.router")
    @patch("fastapi.FastAPI")
    def test_app_initialization(
        self,
        mock_fastapi,
        mock_health_router,
        mock_delivery_router,
        mock_customer_router,
    ):
        # Arrange
        mock_app_instance = MagicMock(spec=FastAPI)
        mock_fastapi.return_value = mock_app_instance

        # Act
        import main  # Import main after mocks are set up

        # Assert
        mock_app_instance.include_router.assert_any_call(mock_customer_router)
        mock_app_instance.include_router.assert_any_call(mock_delivery_router)
        mock_app_instance.include_router.assert_any_call(mock_health_router)


if __name__ == "__main__":
    unittest.main()
