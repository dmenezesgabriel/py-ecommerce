import logging

logger = logging.getLogger("app")
import pika
from pymongo.errors import ServerSelectionTimeoutError


class HealthService:
    def __init__(self, db, rabbitmq_host: str):
        self.db = db
        self.rabbitmq_host = rabbitmq_host

    def check_mongodb(self) -> bool:
        try:
            # Perform a simple MongoDB command to check connection
            self.db.command("ping")
            return True
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False

    def check_rabbitmq(self) -> bool:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rabbitmq_host, heartbeat=120
                )
            )
            connection.close()
            return True
        except Exception as e:
            logger.error(f"RabbitMQ health check failed: {e}")
            return False

    def get_health_status(self) -> dict:
        mongodb_status = self.check_mongodb()
        rabbitmq_status = self.check_rabbitmq()
        return {
            "mongodb": "healthy" if mongodb_status else "unhealthy",
            "rabbitmq": "healthy" if rabbitmq_status else "unhealthy",
        }
