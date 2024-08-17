import logging
import os

import aiohttp

logger = logging.getLogger()


class OrderVerificationService:
    async def verify_order(self, order_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{os.getenv('ORDER_SERVICE_BASE_URL')}/{order_id}"
                ) as response:
                    if response.status == 200:
                        order = await response.json()
                        if order["status"] not in ["canceled"]:
                            return True
            except Exception as e:
                logger.error(f"Error verifying order {order_id}: {e}")
            return False
