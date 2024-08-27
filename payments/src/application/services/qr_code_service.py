import logging
import time
from typing import Tuple

logger = logging.getLogger("app")


class QRCodeService:
    def __init__(self, mercado_pago_access_token: str):
        self.mercado_pago_access_token = mercado_pago_access_token

    def create_qr_code(self, order_id: int, amount: float) -> Tuple[str, int]:
        logger.info(
            f"Mocking QR code creation for order_id: {order_id}, amount: {amount}"
        )

        # Mocked response from MercadoPago API
        qr_code = f"https://www.mercadopago.com.br/qr-code/{order_id}"
        qr_code_expiration = int(time.time()) + 3600  # 1 hour expiration

        return qr_code, qr_code_expiration
