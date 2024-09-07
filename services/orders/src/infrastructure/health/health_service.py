import logging

import pika
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

logger = logging.getLogger("app")


class HealthService:
    def __init__(self, db: Session, rabbitmq_host: str):
        self.db = db
        self.rabbitmq_host = rabbitmq_host

    def check_database(self) -> bool:
        try:
            # Use text() to create a textual SQL expression
            self.db.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
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
        db_status = self.check_database()
        rabbitmq_status = self.check_rabbitmq()
        return {
            "database": "healthy" if db_status else "unhealthy",
            "rabbitmq": "healthy" if rabbitmq_status else "unhealthy",
        }
