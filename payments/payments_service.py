import json
import logging
import os
import threading
import time
from enum import Enum
from typing import List, Optional

import pika
from bson.objectid import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

app = FastAPI(root_path="/payments")

# MongoDB setup
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "payments")
MONGO_USER = os.getenv("MONGO_USER", "mongo")
MONGO_PASS = os.getenv("MONGO_PASS", "mongo")

client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASS,
)
db = client[MONGO_DB]
payments_collection = db["payments"]

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Custom Exceptions
class EntityNotFound(Exception):
    pass


class EntityAlreadyExists(Exception):
    pass


class InvalidAction(Exception):
    pass


# Entities
class PaymentEntity:
    def __init__(
        self,
        order_id: int,
        amount: float,
        status: str,
        id: Optional[str] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.status = status

    def update_status(self, new_status: str):
        self.status = new_status


# Services
class PaymentService:
    def __init__(self, payment_repository, payment_publisher):
        self.payment_repository = payment_repository
        self.payment_publisher = payment_publisher

    def create_payment(
        self, order_id: int, amount: float, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_order_id(order_id)
        if payment:
            raise EntityAlreadyExists(
                f"Payment with order_id '{order_id}' already exists"
            )

        payment_entity = PaymentEntity(
            order_id=order_id, amount=amount, status=status
        )
        self.payment_repository.save(payment_entity)
        return payment_entity

    def get_payment_by_id(self, payment_id: str) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")
        return payment

    def get_payment_by_order_id(self, order_id: int) -> PaymentEntity:
        payment = self.payment_repository.find_by_order_id(order_id)
        if not payment:
            raise EntityNotFound(
                f"Payment with order_id '{order_id}' not found"
            )
        return payment

    def update_payment(
        self, payment_id: str, order_id: int, amount: float, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        if payment.status == PaymentStatus.CANCELED.value:
            raise InvalidAction("Cannot modify a canceled payment")

        payment.order_id = order_id
        payment.amount = amount
        payment.status = status
        self.payment_repository.save(payment)
        return payment

    def update_payment_status(
        self, payment_id: str, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        if payment.status == PaymentStatus.CANCELED.value:
            raise InvalidAction(
                "Cannot change the status of a canceled payment"
            )

        if (
            status
            in [
                PaymentStatus.COMPLETED.value,
                PaymentStatus.FAILED.value,
                PaymentStatus.REFUNDED.value,
            ]
            and payment.status == PaymentStatus.CANCELED.value
        ):
            raise InvalidAction(
                f"Cannot {status.lower()} a payment that has been canceled"
            )

        payment.update_status(status)
        self.payment_repository.save(payment)

        # Publish the status update
        self.payment_publisher.publish_payment_update(
            payment_id=payment.id,
            order_id=payment.order_id,
            status=payment.status,
        )

        return payment

    def cancel_payment(self, payment_id: str) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        if payment.status in [
            PaymentStatus.COMPLETED.value,
            PaymentStatus.FAILED.value,
            PaymentStatus.REFUNDED.value,
            PaymentStatus.CANCELED.value,
        ]:
            raise InvalidAction(
                "Cannot cancel a payment that has been completed, failed, refunded, or already canceled"
            )

        payment.update_status(PaymentStatus.CANCELED.value)
        self.payment_repository.save(payment)

        # Publish the status update
        self.payment_publisher.publish_payment_update(
            payment_id=payment.id,
            order_id=payment.order_id,
            status=payment.status,
        )

        return payment

    def delete_payment(self, payment_id: str):
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        self.payment_repository.delete(payment)
        return payment


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


# Ports (Interfaces)
class PaymentRepository:
    def save(self, payment: PaymentEntity):
        raise NotImplementedError

    def find_by_id(self, payment_id: str) -> Optional[PaymentEntity]:
        raise NotImplementedError

    def find_by_order_id(self, order_id: int) -> Optional[PaymentEntity]:
        raise NotImplementedError

    def delete(self, payment: PaymentEntity):
        raise NotImplementedError


# Adapters (Repository Implementation)
class MongoDBPaymentRepository(PaymentRepository):
    def __init__(self, db):
        self.db = db

    def save(self, payment: PaymentEntity):
        if payment.id:
            self.db.replace_one(
                {"_id": ObjectId(payment.id)}, payment.__dict__
            )
        else:
            result = self.db.insert_one(payment.__dict__)
            payment.id = str(result.inserted_id)

    def find_by_id(self, payment_id: str) -> Optional[PaymentEntity]:
        payment_data = self.db.find_one({"_id": ObjectId(payment_id)})
        if payment_data:
            return PaymentEntity(
                id=str(payment_data["_id"]),
                order_id=payment_data["order_id"],
                amount=payment_data["amount"],
                status=payment_data["status"],
            )
        return None

    def find_by_order_id(self, order_id: int) -> Optional[PaymentEntity]:
        payment_data = self.db.find_one({"order_id": order_id})
        if payment_data:
            return PaymentEntity(
                id=str(payment_data["_id"]),
                order_id=payment_data["order_id"],
                amount=payment_data["amount"],
                status=payment_data["status"],
            )
        return None

    def delete(self, payment: PaymentEntity):
        self.db.delete_one({"_id": ObjectId(payment.id)})


# Publisher Adapter using Pika
class BaseMessagingAdapter:
    def __init__(self, connection_params, max_retries=5, delay=5):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        attempts = 0
        while attempts < self.max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    self.connection_params
                )
                self.channel = self.connection.channel()
                return
            except pika.exceptions.AMQPConnectionError as e:
                attempts += 1
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} to connect to RabbitMQ failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        raise pika.exceptions.AMQPConnectionError(
            "Failed to connect to RabbitMQ after multiple attempts."
        )


class PaymentPublisher(BaseMessagingAdapter):
    def __init__(self, connection_params, max_retries=5, delay=5):
        super().__init__(connection_params, max_retries, delay)
        self.exchange_name = "payment_exchange"

    def publish_payment_update(
        self, payment_id: str, order_id: int, status: str
    ):
        message = json.dumps(
            {
                "payment_id": payment_id,
                "order_id": order_id,
                "status": status,
            }
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="payment_queue",
                body=message,
            )
            logger.info(
                f"Published payment update: {message} to payment_queue"
            )
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_payment_update(payment_id, order_id, status)


class OrderSubscriber(BaseMessagingAdapter):
    def __init__(
        self, payment_service: PaymentService, max_retries=5, delay=5
    ):
        self.payment_service = payment_service
        connection_params = pika.ConnectionParameters(
            host="rabbitmq", heartbeat=120
        )
        super().__init__(connection_params, max_retries, delay)

    def start_consuming(self):
        self.channel.exchange_declare(
            exchange="orders_exchange", exchange_type="topic", durable=True
        )
        self.channel.queue_declare(queue="orders_queue", durable=True)
        self.channel.queue_bind(
            exchange="orders_exchange",
            queue="orders_queue",
            routing_key="orders_queue",
        )

        self.channel.basic_consume(
            queue="orders_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )

        logger.info("Starting to consume messages from orders_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from orders_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            order_id = data.get("order_id")
            status = data.get("status")
            amount = data.get("amount")

            if status == "canceled":
                payment = self.payment_service.get_payment_by_order_id(
                    order_id
                )
                if payment.status in ["failed", "refunded", "canceled"]:
                    return
                self.payment_service.cancel_payment(payment.id)
                logger.info(f"Canceled payment for order ID: {order_id}.")

            if status == "confirmed":
                self.payment_service.create_payment(
                    order_id=order_id, amount=amount, status="pending"
                )
                logger.info(
                    f"Created pending payment for order ID: {order_id}."
                )
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)


# FastAPI Routes (Adapter)
@app.on_event("startup")
def on_startup():
    # Clear all existing data
    payments_collection.delete_many(
        {}
    )  # Clear all documents from the collection

    # Start the subscriber for order messages
    payment_service = get_payment_service()
    order_subscriber = OrderSubscriber(payment_service)
    threading.Thread(target=order_subscriber.start_consuming).start()


def get_payment_service() -> PaymentService:
    payment_repository = MongoDBPaymentRepository(payments_collection)
    payment_publisher = get_payment_publisher()
    return PaymentService(payment_repository, payment_publisher)


def get_payment_publisher() -> PaymentPublisher:
    connection_params = pika.ConnectionParameters(
        host="rabbitmq", heartbeat=120
    )
    return PaymentPublisher(connection_params)


def get_health_service() -> HealthService:
    return HealthService(db, rabbitmq_host="rabbitmq")


# Pydantic Models for API
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELED = "canceled"


class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    status: PaymentStatus

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "order_id": 1,
                    "amount": 100.00,
                    "status": "pending",
                },
                {
                    "order_id": 2,
                    "amount": 250.75,
                    "status": "completed",
                },
            ]
        }


class PaymentUpdate(BaseModel):
    order_id: int
    amount: float
    status: PaymentStatus

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "order_id": 1,
                    "amount": 100.00,
                    "status": "completed",
                },
                {
                    "order_id": 2,
                    "amount": 250.75,
                    "status": "failed",
                },
            ]
        }


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus

    class Config:
        json_schema_extra = {
            "examples": [
                {"status": "completed"},
                {"status": "canceled"},
            ]
        }


class PaymentResponse(BaseModel):
    id: str
    order_id: int
    amount: float
    status: PaymentStatus

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: str,
        }
        json_schema_extra = {
            "examples": [
                {
                    "id": "64c8cbe2f3a5e9a1c4b63e29",
                    "order_id": 1,
                    "amount": 100.00,
                    "status": "completed",
                },
                {
                    "id": "64c8cbe2f3a5e9a1c4b63e30",
                    "order_id": 2,
                    "amount": 250.75,
                    "status": "pending",
                },
            ]
        }


@app.post("/payments/", tags=["Payments"], response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        created_payment = service.create_payment(
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        return serialize_payment(created_payment)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/payments/", tags=["Payments"], response_model=List[PaymentResponse])
def read_payments(service: PaymentService = Depends(get_payment_service)):
    payments = service.payment_repository.db.find()
    return [
        serialize_payment(
            PaymentEntity(
                id=str(payment["_id"]),
                order_id=payment["order_id"],
                amount=payment["amount"],
                status=payment["status"],
            )
        )
        for payment in payments
    ]


@app.get(
    "/payments/{payment_id}", tags=["Payments"], response_model=PaymentResponse
)
def read_payment(
    payment_id: str, service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = service.get_payment_by_id(payment_id)
        return serialize_payment(payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/payments/by-order-id/{order_id}",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def read_payment_by_order_id(
    order_id: int, service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = service.get_payment_by_order_id(order_id)
        return serialize_payment(payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put(
    "/payments/{payment_id}", tags=["Payments"], response_model=PaymentResponse
)
def update_payment(
    payment_id: str,
    payment: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment(
            payment_id=payment_id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/payments/{payment_id}/status",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def update_payment_status(
    payment_id: str,
    status_update: PaymentStatusUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment_status(
            payment_id, status_update.status
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/payments/{payment_id}/complete",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def complete_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment_status(
            payment_id, PaymentStatus.COMPLETED.value
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/payments/{payment_id}/fail",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def fail_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment_status(
            payment_id, PaymentStatus.FAILED.value
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/payments/{payment_id}/refund",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def refund_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment_status(
            payment_id, PaymentStatus.REFUNDED.value
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/payments/{payment_id}/cancel",
    tags=["Payments"],
    response_model=PaymentResponse,
)
def cancel_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        canceled_payment = service.cancel_payment(payment_id)
        return serialize_payment(canceled_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidAction as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/payments/{payment_id}", tags=["Payments"])
def delete_payment(
    payment_id: str, service: PaymentService = Depends(get_payment_service)
):
    try:
        service.delete_payment(payment_id)
        return {"detail": "Payment deleted"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/health", tags=["Health"])
def health_check(health_service: HealthService = Depends(get_health_service)):
    return health_service.get_health_status()


# Serialization Function
def serialize_payment(payment: PaymentEntity) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        status=payment.status,
    )
