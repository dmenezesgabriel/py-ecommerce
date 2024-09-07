import time
from unittest.mock import MagicMock, patch

from src.application.services.qr_code_service import QRCodeService


@patch("src.application.services.qr_code_service.logger")
@patch("src.application.services.qr_code_service.time")
def test_create_qr_code(mock_time, mock_logger):
    # Arrange
    mercado_pago_access_token = "fake_token"
    qr_code_service = QRCodeService(mercado_pago_access_token)
    order_id = 123
    amount = 250.75

    # Mock the current time
    mock_time.time.return_value = 1609459200  # Mocked timestamp

    # Act
    qr_code, qr_code_expiration = qr_code_service.create_qr_code(
        order_id, amount
    )

    # Assert
    expected_qr_code = f"https://www.mercadopago.com.br/qr-code/{order_id}"
    expected_expiration = 1609459200 + 3600  # 1 hour expiration

    assert qr_code == expected_qr_code
    assert qr_code_expiration == expected_expiration

    # Verify logging
    mock_logger.info.assert_called_once_with(
        f"Mocking QR code creation for order_id: {order_id}, amount: {amount}"
    )
    mock_time.time.assert_called_once()  # Verify time.time() was called


def test_qr_code_service_initialization():
    # Arrange
    mercado_pago_access_token = "fake_token"

    # Act
    qr_code_service = QRCodeService(mercado_pago_access_token)

    # Assert
    assert (
        qr_code_service.mercado_pago_access_token == mercado_pago_access_token
    )
