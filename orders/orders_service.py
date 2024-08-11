import json
import logging
import os
import threading
import time
import uuid
from enum import Enum as PyEnum
from typing import List, Optional

import aiohttp
import pika
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./data/order.db"

# Ensure the data directory exists
if not os.path.exists("/app/data"):
    os.makedirs("/app/data")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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


class InvalidEntity(Exception):
    pass


# Entities
class OrderStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"
    PAID = "paid"  # New status added


class CustomerEntity:
    def __init__(self, name: str, email: str, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.email = email


class OrderItemEntity:
    def __init__(
        self, product_sku: str, quantity: int, id: Optional[int] = None
    ):
        self.id = id
        self.product_sku = product_sku
        self.quantity = quantity


class OrderEntity:
    def __init__(
        self,
        customer: CustomerEntity,
        order_items: List[OrderItemEntity],
        status: OrderStatus = OrderStatus.PENDING,
        id: Optional[int] = None,
    ):
        self.id = id
        self.order_number = str(uuid.uuid4())
        self.customer = customer
        self.order_items = order_items
        self.status = status

    def add_item(self, order_item: OrderItemEntity):
        self.order_items.append(order_item)

    def update_status(self, new_status: OrderStatus):
        self.status = new_status


# Ports (Interfaces)
class OrderRepository:
    def save(self, order: OrderEntity):
        raise NotImplementedError

    def find_by_id(self, order_id: int) -> Optional[OrderEntity]:
        raise NotImplementedError

    def find_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        raise NotImplementedError

    def delete(self, order: OrderEntity):
        raise NotImplementedError

    def list_all(self) -> List[OrderEntity]:
        raise NotImplementedError


class CustomerRepository:
    def save(self, customer: CustomerEntity):
        raise NotImplementedError

    def find_by_email(self, email: str) -> Optional[CustomerEntity]:
        raise NotImplementedError

    def list_all(self) -> List[CustomerEntity]:
        raise NotImplementedError


# Adapters
# SQLAlchemy Mappers and Repositories
class CustomerModel(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    orders = relationship("OrderModel", back_populates="customer")


class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(
        String, unique=True, index=True, default=lambda: str(uuid.uuid4())
    )
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    customer = relationship("CustomerModel", back_populates="orders")
    order_items = relationship(
        "OrderItemModel", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_sku = Column(String, index=True)
    quantity = Column(Integer)
    order = relationship("OrderModel", back_populates="order_items")


class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, order: OrderEntity):
        customer_model = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == order.customer.email)
            .first()
        )
        if not customer_model:
            customer_model = CustomerModel(
                name=order.customer.name, email=order.customer.email
            )
            self.db.add(customer_model)
            self.db.commit()
            self.db.refresh(customer_model)

        if order.id:
            db_order = (
                self.db.query(OrderModel)
                .filter(OrderModel.id == order.id)
                .first()
            )
            db_order.status = order.status
        else:
            db_order = OrderModel(
                order_number=order.order_number,
                customer_id=customer_model.id,
                status=order.status,
            )
            self.db.add(db_order)
            self.db.commit()
            self.db.refresh(db_order)

        self.db.query(OrderItemModel).filter(
            OrderItemModel.order_id == db_order.id
        ).delete()

        for item in order.order_items:
            db_order_item = OrderItemModel(
                order_id=db_order.id,
                product_sku=item.product_sku,
                quantity=item.quantity,
            )
            self.db.add(db_order_item)

        self.db.commit()
        self.db.refresh(db_order)
        order.id = db_order.id
        order.customer.id = customer_model.id

    def find_by_id(self, order_id: int) -> Optional[OrderEntity]:
        db_order = (
            self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        )
        if db_order:
            customer = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.id == db_order.customer_id)
                .first()
            )
            order_items = (
                self.db.query(OrderItemModel)
                .filter(OrderItemModel.order_id == db_order.id)
                .all()
            )
            return OrderEntity(
                id=db_order.id,
                customer=CustomerEntity(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                ),
                order_items=[
                    OrderItemEntity(
                        id=item.id,
                        product_sku=item.product_sku,
                        quantity=item.quantity,
                    )
                    for item in order_items
                ],
                status=db_order.status,
            )
        return None

    def find_by_order_number(self, order_number: str) -> Optional[OrderEntity]:
        db_order = (
            self.db.query(OrderModel)
            .filter(OrderModel.order_number == order_number)
            .first()
        )
        if db_order:
            customer = (
                self.db.query(CustomerModel)
                .filter(CustomerModel.id == db_order.customer_id)
                .first()
            )
            order_items = (
                self.db.query(OrderItemModel)
                .filter(OrderItemModel.order_id == db_order.id)
                .all()
            )
            return OrderEntity(
                id=db_order.id,
                customer=CustomerEntity(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                ),
                order_items=[
                    OrderItemEntity(
                        id=item.id,
                        product_sku=item.product_sku,
                        quantity=item.quantity,
                    )
                    for item in order_items
                ],
                status=db_order.status,
            )
        return None

    def delete(self, order: OrderEntity):
        db_order = (
            self.db.query(OrderModel).filter(OrderModel.id == order.id).first()
        )
        if db_order:
            self.db.delete(db_order)
            self.db.commit()

    def list_all(self) -> List[OrderEntity]:
        db_orders = self.db.query(OrderModel).all()
        return [
            OrderEntity(
                id=db_order.id,
                customer=CustomerEntity(
                    id=db_order.customer.id,
                    name=db_order.customer.name,
                    email=db_order.customer.email,
                ),
                order_items=[
                    OrderItemEntity(
                        id=item.id,
                        product_sku=item.product_sku,
                        quantity=item.quantity,
                    )
                    for item in db_order.order_items
                ],
                status=db_order.status,
            )
            for db_order in db_orders
        ]


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, customer: CustomerEntity):
        db_customer = CustomerModel(name=customer.name, email=customer.email)
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        customer.id = db_customer.id

    def find_by_email(self, email: str) -> Optional[CustomerEntity]:
        db_customer = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == email)
            .first()
        )
        if db_customer:
            return CustomerEntity(
                id=db_customer.id,
                name=db_customer.name,
                email=db_customer.email,
            )
        return None

    def list_all(self) -> List[CustomerEntity]:
        db_customers = self.db.query(CustomerModel).all()
        return [
            CustomerEntity(
                id=db_customer.id,
                name=db_customer.name,
                email=db_customer.email,
            )
            for db_customer in db_customers
        ]


# Publisher Adapter using Pika
class InventoryPublisher:
    def __init__(self, connection_params, max_retries=5, delay=5):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None
        self.channel = None
        self.exchange_name = "inventory_exchange"
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
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        raise pika.exceptions.AMQPConnectionError(
            "Failed to connect to RabbitMQ after multiple attempts."
        )

    def publish_inventory_update(self, sku: str, action: str, quantity: int):
        message = json.dumps(
            {
                "sku": sku,
                "action": action,
                "quantity": quantity,
            }
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="inventory_queue",
                body=message,
            )
            logger.info(f"Published inventory update: {message}")
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_inventory_update(sku, action, quantity)


class OrderUpdatePublisher:
    def __init__(self, connection_params, max_retries=5, delay=5):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None
        self.channel = None
        self.exchange_name = "orders_exchange"
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
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        raise pika.exceptions.AMQPConnectionError(
            "Failed to connect to RabbitMQ after multiple attempts."
        )

    def publish_order_update(self, order_id: int, amount: float, status: str):
        message = json.dumps(
            {
                "order_id": order_id,
                "amount": amount,
                "status": status,
            }
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="orders_queue",
                body=message,
            )
            logger.info(f"Published order update: {message} to orders_queue")
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_order_update(order_id, amount, status)


# Subscriber Adapter using Pika
class PaymentSubscriber:

    def __init__(
        self,
        order_service: "OrderService",
        max_retries: int = 5,
        delay: int = 5,
    ):
        self.order_service = order_service
        self.connection_params = pika.ConnectionParameters(host="rabbitmq")
        self.max_retries = max_retries
        self.delay = delay

    def connect(self):
        attempts = 0
        while attempts < self.max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    self.connection_params
                )
                self.channel = self.connection.channel()
                return True
            except pika.exceptions.AMQPConnectionError as e:
                attempts += 1
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        return False

    def start_consuming(self):
        if not self.connect():
            logger.error("Failed to start consuming. Exiting.")
            return

        self.channel.exchange_declare(
            exchange="payment_exchange", exchange_type="topic", durable=True
        )
        self.channel.queue_declare(queue="payment_queue", durable=True)
        self.channel.queue_bind(
            exchange="payment_exchange",
            queue="payment_queue",
            routing_key="payment_queue",
        )

        self.channel.basic_consume(
            queue="payment_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )

        logger.info("Starting to consume messages from payment_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from payment_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            order_id = data.get("order_id")
            status = data.get("status")

            if status == "completed":
                self.order_service.set_paid_order(order_id)
                logger.info(f"Order ID {order_id} marked as paid.")
            if status in ["refunded", "canceled"]:
                self.order_service.cancel_order(order_id)
                logger.info(f"Order ID {order_id} marked as canceled.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)


class DeliverySubscriber:

    def __init__(
        self,
        order_service: "OrderService",
        max_retries: int = 5,
        delay: int = 5,
    ):
        self.order_service = order_service
        self.connection_params = pika.ConnectionParameters(host="rabbitmq")
        self.max_retries = max_retries
        self.delay = delay

    def connect(self):
        attempts = 0
        while attempts < self.max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    self.connection_params
                )
                self.channel = self.connection.channel()
                return True
            except pika.exceptions.AMQPConnectionError as e:
                attempts += 1
                logger.error(
                    f"Attempt {attempts}/{self.max_retries} failed: {str(e)}"
                )
                time.sleep(self.delay)

        logger.error("Max retries exceeded. Could not connect to RabbitMQ.")
        return False

    def start_consuming(self):
        if not self.connect():
            logger.error("Failed to start consuming. Exiting.")
            return

        self.channel.exchange_declare(
            exchange="delivery_exchange", exchange_type="topic", durable=True
        )
        self.channel.queue_declare(queue="delivery_queue", durable=True)
        self.channel.queue_bind(
            exchange="delivery_exchange",
            queue="delivery_queue",
            routing_key="delivery_queue",
        )

        self.channel.basic_consume(
            queue="delivery_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )

        logger.info("Starting to consume messages from delivery_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from delivery_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            order_id = data.get("order_id")
            status = data.get("status")

            if status == "in_transit":
                self.order_service.update_order_status(
                    order_id, OrderStatus.SHIPPED
                )
                logger.info(f"Order ID {order_id} marked as shipped.")
            if status == "delivered":
                self.order_service.update_order_status(
                    order_id, OrderStatus.DELIVERED
                )
                logger.info(f"Order ID {order_id} marked as delivered.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)


# Services
class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        customer_repository: CustomerRepository,
        inventory_publisher: InventoryPublisher,
        order_update_publisher: OrderUpdatePublisher,
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.inventory_publisher = inventory_publisher
        self.order_update_publisher = order_update_publisher

    async def create_order(
        self, customer: CustomerEntity, order_items: List[OrderItemEntity]
    ) -> OrderEntity:
        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        order = OrderEntity(
            customer=existing_customer,
            order_items=order_items,
        )

        try:
            for item in order_items:
                self.inventory_publisher.publish_inventory_update(
                    item.product_sku, "subtract", item.quantity
                )

            self.order_repository.save(order)
            total_amount = await self.calculate_order_total(order)
            return order, total_amount

        except Exception as e:
            for item in order_items:
                self.inventory_publisher.publish_inventory_update(
                    item.product_sku, "add", item.quantity
                )
            raise e

    def get_order_by_id(self, order_id: int) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")
        return order

    def get_order_by_order_number(self, order_number: str) -> OrderEntity:
        order = self.order_repository.find_by_order_number(order_number)
        if not order:
            raise EntityNotFound(
                f"Order with Order Number '{order_number}' not found"
            )
        return order

    async def update_order(
        self,
        order_id: int,
        customer: CustomerEntity,
        order_items: List[OrderItemEntity],
    ) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        inventory_changes = []

        try:
            current_order_items = {
                item.product_sku: item.quantity for item in order.order_items
            }

            for item in order_items:
                if item.product_sku in current_order_items:
                    old_quantity = current_order_items[item.product_sku]
                    if item.quantity > old_quantity:
                        diff = item.quantity - old_quantity
                        self.inventory_publisher.publish_inventory_update(
                            item.product_sku, "subtract", diff
                        )
                        inventory_changes.append((item.product_sku, diff))
                    elif item.quantity < old_quantity:
                        diff = old_quantity - item.quantity
                        self.inventory_publisher.publish_inventory_update(
                            item.product_sku, "add", diff
                        )
                        inventory_changes.append((item.product_sku, -diff))
                else:
                    self.inventory_publisher.publish_inventory_update(
                        item.product_sku,
                        "subtract",
                        item.quantity,
                    )
                    inventory_changes.append((item.product_sku, item.quantity))

            order.customer = existing_customer
            order.order_items = order_items
            self.order_repository.save(order)
            total_amount = await self.calculate_order_total(order)
            return order, total_amount

        except Exception as e:
            for sku, quantity in inventory_changes:
                action = "add" if quantity > 0 else "subtract"
                self.inventory_publisher.publish_inventory_update(
                    sku, action, abs(quantity)
                )
            raise e

    def update_order_status(
        self, order_id: int, status: OrderStatus
    ) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        order.update_status(status)
        self.order_repository.save(order)
        return order

    def set_paid_order(self, order_id: int):
        """Sets the order status to PAID."""
        order = self.get_order_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")
        order.update_status(OrderStatus.PAID)
        self.order_repository.save(order)

    async def confirm_order(self, order_id: int) -> OrderEntity:
        order = self.get_order_by_id(order_id)
        if order.status != OrderStatus.PENDING:
            raise InvalidEntity("Only pending orders can be confirmed")

        order.update_status(OrderStatus.CONFIRMED)
        self.order_repository.save(order)
        try:
            total_amount = await self.calculate_order_total(order)
            self.order_update_publisher.publish_order_update(
                order_id=order.id,
                amount=total_amount,
                status=order.status.value,
            )
        except Exception as e:
            raise e
        return order

    def cancel_order(self, order_id: int) -> OrderEntity:
        order = self.get_order_by_id(order_id)
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise InvalidEntity(
                "Only pending or confirmed orders can be canceled"
            )

        for item in order.order_items:
            self.inventory_publisher.publish_inventory_update(
                item.product_sku, "add", item.quantity
            )

        order.update_status(OrderStatus.CANCELED)
        self.order_repository.save(order)
        try:
            self.order_update_publisher.publish_order_update(
                order_id=order.id, amount=0.0, status=order.status.value
            )
        except Exception as e:
            raise e
        return order

    def delete_order(self, order_id: int) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        self.order_repository.delete(order)
        return order

    def list_orders(self) -> List[OrderEntity]:
        return self.order_repository.list_all()

    async def calculate_order_total(self, order: OrderEntity) -> float:
        total_amount = 0.0
        async with aiohttp.ClientSession() as session:
            for item in order.order_items:
                async with session.get(
                    f"http://inventory_service:8001/products/{item.product_sku}"
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Product {item.product_sku} not found",
                        )
                    product = await response.json()
                    total_amount += product["price"] * item.quantity
        return total_amount


# FastAPI Routes (Adapter)
@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    order_repository = SQLAlchemyOrderRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    inventory_publisher = get_inventory_publisher()
    order_update_publisher = get_order_update_publisher()
    order_service = OrderService(
        order_repository,
        customer_repository,
        inventory_publisher,
        order_update_publisher,
    )

    payment_subscriber = PaymentSubscriber(order_service)
    delivery_subscriber = DeliverySubscriber(order_service)
    threading.Thread(target=payment_subscriber.start_consuming).start()
    threading.Thread(target=delivery_subscriber.start_consuming).start()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_inventory_publisher() -> InventoryPublisher:
    connection_params = pika.ConnectionParameters(host="rabbitmq")
    return InventoryPublisher(connection_params)


def get_order_update_publisher() -> OrderUpdatePublisher:
    connection_params = pika.ConnectionParameters(host="rabbitmq")
    return OrderUpdatePublisher(connection_params)


def get_order_service(
    db: Session = Depends(get_db),
    inventory_publisher: InventoryPublisher = Depends(get_inventory_publisher),
    order_update_publisher: OrderUpdatePublisher = Depends(
        get_order_update_publisher
    ),
) -> OrderService:
    order_repository = SQLAlchemyOrderRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    return OrderService(
        order_repository,
        customer_repository,
        inventory_publisher,
        order_update_publisher,
    )


# Pydantic Models for API
class OrderItemCreate(BaseModel):
    product_sku: str
    quantity: int

    class Config:
        json_schema_extra = {
            "examples": [{"product_sku": "ABC123", "quantity": 2}]
        }


class CustomerCreate(BaseModel):
    name: str
    email: str

    class Config:
        json_schema_extra = {
            "examples": [{"name": "John Doe", "email": "john.doe@example.com"}]
        }


class OrderCreate(BaseModel):
    customer: CustomerCreate
    order_items: List[OrderItemCreate] = []

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "customer": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                    },
                    "order_items": [
                        {"product_sku": "ABC123", "quantity": 2},
                        {"product_sku": "XYZ456", "quantity": 1},
                    ],
                }
            ]
        }


class OrderItemResponse(BaseModel):
    product_sku: str
    quantity: int

    class Config:
        orm_mode = True


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer: CustomerResponse
    order_items: List[OrderItemResponse]
    status: OrderStatus
    total_amount: float

    class Config:
        orm_mode = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


@app.post("/orders/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate, service: OrderService = Depends(get_order_service)
):
    customer_entity = CustomerEntity(
        name=order.customer.name, email=order.customer.email
    )
    order_items = [
        OrderItemEntity(product_sku=item.product_sku, quantity=item.quantity)
        for item in order.order_items
    ]
    created_order, total_amount = await service.create_order(
        customer_entity, order_items
    )
    return serialize_order(created_order, total_amount)


@app.get("/orders/", response_model=List[OrderResponse])
async def read_orders(service: OrderService = Depends(get_order_service)):
    orders = service.list_orders()
    orders_with_amounts = [
        {"order": order, "amount": await service.calculate_order_total(order)}
        for order in orders
    ]
    return [
        serialize_order(order["order"], order["amount"])
        for order in orders_with_amounts
    ]


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        order = service.get_order_by_id(order_id)
        total_amount = await service.calculate_order_total(order)
        return serialize_order(order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/orders/by-order-number/{order_number}", response_model=OrderResponse
)
async def read_order_by_order_number(
    order_number: str, service: OrderService = Depends(get_order_service)
):
    try:
        order = service.get_order_by_order_number(order_number)
        total_amount = await service.calculate_order_total(order)
        return serialize_order(order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    customer_entity = CustomerEntity(
        name=order.customer.name, email=order.customer.email
    )
    order_items = [
        OrderItemEntity(product_sku=item.product_sku, quantity=item.quantity)
        for item in order.order_items
    ]
    try:
        updated_order, total_amount = await service.update_order(
            order_id, customer_entity, order_items
        )
        return serialize_order(updated_order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
):
    try:
        updated_order = service.update_order_status(
            order_id, status_update.status
        )
        total_amount = await service.calculate_order_total(updated_order)
        return serialize_order(updated_order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/orders/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        confirmed_order = await service.confirm_order(order_id)
        total_amount = await service.calculate_order_total(confirmed_order)
        return serialize_order(confirmed_order, total_amount)
    except (EntityNotFound, InvalidEntity) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        canceled_order = service.cancel_order(order_id)
        total_amount = await service.calculate_order_total(canceled_order)
        return serialize_order(canceled_order, total_amount)
    except (EntityNotFound, InvalidEntity) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/orders/{order_id}", status_code=204)
async def delete_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        service.delete_order(order_id)
        return {"message": "Order deleted successfully"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/customers/", response_model=List[CustomerResponse])
async def read_customers(service: OrderService = Depends(get_order_service)):
    customers = service.customer_repository.list_all()
    return [serialize_customer(customer) for customer in customers]


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
async def read_customer(
    customer_id: int, service: OrderService = Depends(get_order_service)
):
    customer = service.customer_repository.find_by_email(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return serialize_customer(customer)


@app.post("/customers/", response_model=CustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    service: OrderService = Depends(get_order_service),
):
    customer_entity = CustomerEntity(name=customer.name, email=customer.email)
    service.customer_repository.save(customer_entity)
    return serialize_customer(customer_entity)


@app.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerCreate,
    service: OrderService = Depends(get_order_service),
):
    customer_entity = service.customer_repository.find_by_email(customer.email)
    if not customer_entity:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_entity.name = customer.name
    customer_entity.email = customer.email
    service.customer_repository.save(customer_entity)
    return serialize_customer(customer_entity)


@app.delete("/customers/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int, service: OrderService = Depends(get_order_service)
):
    customer_entity = service.customer_repository.find_by_email(customer_id)
    if not customer_entity:
        raise HTTPException(status_code=404, detail="Customer not found")
    service.customer_repository.delete(customer_entity)


# Serialization Functions
def serialize_order(order: OrderEntity, total_amount: float) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer=serialize_customer(order.customer),
        order_items=[serialize_order_item(item) for item in order.order_items],
        status=order.status,
        total_amount=total_amount,
    )


def serialize_order_item(order_item: OrderItemEntity) -> OrderItemResponse:
    return OrderItemResponse(
        product_sku=order_item.product_sku,
        quantity=order_item.quantity,
    )


def serialize_customer(customer: CustomerEntity) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
    )
