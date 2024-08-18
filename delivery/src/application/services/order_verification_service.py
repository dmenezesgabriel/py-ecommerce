import logging

import aiohttp
from src.config import Config

logger = logging.getLogger("app")


class OrderVerificationService:
    async def verify_order(self, order_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{Config.ORDER_SERVICE_BASE_URL}/orders/{order_id}"
                logger.info(f"Verifying order: {url}")
                async with session.get(url) as response:
                    if response.status == 200:
                        order = await response.json()
                        if order["status"] not in ["canceled"]:
                            return True
            except Exception as e:
                logger.error(f"Error verifying order {order_id}: {e}")
            return False
