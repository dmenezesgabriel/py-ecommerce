import json
import logging
import os
import time
from enum import Enum
from typing import List, Optional

import aiohttp
import pika
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.sql import text  # Import the text function

app = FastAPI()

# Database Configuration
DATABASE_URL = "sqlite:///./data/deliveries.db"

# Ensure the data directory exists
if not os.path.exists("./data"):
    os.makedirs("./data")

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


class InvalidOperation(Exception):
    pass


# Entities
class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class CustomerEntity:
    def __init__(self, name: str, email: str, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.email = email


class AddressEntity:
    def __init__(
        self,
        city: str,
        state: str,
        country: str,
        zip_code: str,
        id: Optional[int] = None,
    ):
        self.id = id
        self.city = city
        self.state = state
        self.country = country
        self.zip_code = zip_code


class DeliveryEntity:
    def __init__(
        self,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
        id: Optional[int] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.delivery_address = delivery_address
        self.delivery_date = delivery_date
        self.status = status
        self.customer = customer
        self.address = address

    def update_status(self, new_status: DeliveryStatus):
        self.status = new_status


# Ports (Interfaces)
class DeliveryRepository:
    def save(self, delivery: DeliveryEntity):
        raise NotImplementedError

    def find_by_id(self, delivery_id: int) -> Optional[DeliveryEntity]:
        raise NotImplementedError

    def find_by_order_id(self, order_id: int) -> Optional[DeliveryEntity]:
        raise NotImplementedError

    def delete(self, delivery: DeliveryEntity):
        raise NotImplementedError

    def list_all(self) -> List[DeliveryEntity]:
        raise NotImplementedError


class CustomerRepository:
    def save(self, customer: CustomerEntity):
        raise NotImplementedError

    def find_by_email(self, email: str) -> Optional[CustomerEntity]:
        raise NotImplementedError


# Adapters
class DeliveryModel(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    delivery_address = Column(String)
    delivery_date = Column(String)
    status = Column(SQLAEnum(DeliveryStatus), default=DeliveryStatus.PENDING)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    customer = relationship("CustomerModel", back_populates="deliveries")
    address = relationship(
        "AddressModel", uselist=False, back_populates="delivery"
    )


class CustomerModel(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    deliveries = relationship("DeliveryModel", back_populates="customer")


class AddressModel(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    delivery = relationship(
        "DeliveryModel", uselist=False, back_populates="address"
    )


class SQLAlchemyDeliveryRepository(DeliveryRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, delivery: DeliveryEntity):
        customer_model = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == delivery.customer.email)
            .first()
        )
        if not customer_model:
            customer_model = CustomerModel(
                name=delivery.customer.name, email=delivery.customer.email
            )
            self.db.add(customer_model)
            self.db.commit()
            self.db.refresh(customer_model)

        if delivery.id:
            db_delivery = (
                self.db.query(DeliveryModel)
                .filter(DeliveryModel.id == delivery.id)
                .first()
            )
        else:
            db_delivery = DeliveryModel(
                order_id=delivery.order_id,
                delivery_address=delivery.delivery_address,
                delivery_date=delivery.delivery_date,
                status=delivery.status,
                customer_id=customer_model.id,
            )
            self.db.add(db_delivery)
            self.db.commit()
            self.db.refresh(db_delivery)

        address_model = AddressModel(
            city=delivery.address.city,
            state=delivery.address.state,
            country=delivery.address.country,
            zip_code=delivery.address.zip_code,
            delivery=db_delivery,
        )
        self.db.add(address_model)
        self.db.commit()
        self.db.refresh(address_model)

        db_delivery.address = address_model
        self.db.commit()
        self.db.refresh(db_delivery)
        delivery.id = db_delivery.id
        delivery.customer.id = customer_model.id
        delivery.address.id = address_model.id

    def find_by_id(self, delivery_id: int) -> Optional[DeliveryEntity]:
        db_delivery = (
            self.db.query(DeliveryModel)
            .filter(DeliveryModel.id == delivery_id)
            .first()
        )
        if db_delivery:
            return DeliveryEntity(
                id=db_delivery.id,
                order_id=db_delivery.order_id,
                delivery_address=db_delivery.delivery_address,
                delivery_date=db_delivery.delivery_date,
                status=db_delivery.status,
                customer=CustomerEntity(
                    id=db_delivery.customer.id,
                    name=db_delivery.customer.name,
                    email=db_delivery.customer.email,
                ),
                address=AddressEntity(
                    id=db_delivery.address.id,
                    city=db_delivery.address.city,
                    state=db_delivery.address.state,
                    country=db_delivery.address.country,
                    zip_code=db_delivery.address.zip_code,
                ),
            )
        return None

    def find_by_order_id(self, order_id: int) -> Optional[DeliveryEntity]:
        db_delivery = (
            self.db.query(DeliveryModel)
            .filter(DeliveryModel.order_id == order_id)
            .first()
        )
        if db_delivery:
            return DeliveryEntity(
                id=db_delivery.id,
                order_id=db_delivery.order_id,
                delivery_address=db_delivery.delivery_address,
                delivery_date=db_delivery.delivery_date,
                status=db_delivery.status,
                customer=CustomerEntity(
                    id=db_delivery.customer.id,
                    name=db_delivery.customer.name,
                    email=db_delivery.customer.email,
                ),
                address=AddressEntity(
                    id=db_delivery.address.id,
                    city=db_delivery.address.city,
                    state=db_delivery.address.state,
                    country=db_delivery.address.country,
                    zip_code=db_delivery.address.zip_code,
                ),
            )
        return None

    def delete(self, delivery: DeliveryEntity):
        db_delivery = (
            self.db.query(DeliveryModel)
            .filter(DeliveryModel.id == delivery.id)
            .first()
        )
        if db_delivery:
            self.db.delete(db_delivery.address)
            self.db.delete(db_delivery)
            self.db.commit()

    def list_all(self) -> List[DeliveryEntity]:
        db_deliveries = self.db.query(DeliveryModel).all()
        return [
            DeliveryEntity(
                id=db_delivery.id,
                order_id=db_delivery.order_id,
                delivery_address=db_delivery.delivery_address,
                delivery_date=db_delivery.delivery_date,
                status=db_delivery.status,
                customer=CustomerEntity(
                    id=db_delivery.customer.id,
                    name=db_delivery.customer.name,
                    email=db_delivery.customer.email,
                ),
                address=AddressEntity(
                    id=db_delivery.address.id,
                    city=db_delivery.address.city,
                    state=db_delivery.address.state,
                    country=db_delivery.address.country,
                    zip_code=db_delivery.address.zip_code,
                ),
            )
            for db_delivery in db_deliveries
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


# Publisher Adapter using Pika
class DeliveryPublisher:
    def __init__(self, connection_params, max_retries=5, delay=5):
        self.connection_params = connection_params
        self.max_retries = max_retries
        self.delay = delay
        self.connection = None
        self.channel = None
        self.exchange_name = "delivery_exchange"
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

    def publish_delivery_update(
        self, delivery_id: int, order_id: int, status: str
    ):
        message = json.dumps(
            {
                "delivery_id": delivery_id,
                "order_id": order_id,
                "status": status,
            }
        )
        try:
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key="delivery_queue",
                body=message,
            )
            logger.info(
                f"Published delivery update: {message} to delivery_queue"
            )
        except pika.exceptions.ConnectionClosed:
            logger.error("Connection closed, attempting to reconnect.")
            self.connect()
            self.publish_delivery_update(delivery_id, order_id, status)


# Service for Order Verification using aiohttp
class OrderVerificationService:
    async def verify_order(self, order_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"http://orders_service:8002/orders/{order_id}"
                ) as response:
                    if response.status == 200:
                        order = await response.json()
                        if order["status"] not in ["canceled"]:
                            return True
            except Exception as e:
                logger.error(f"Error verifying order {order_id}: {e}")
            return False


# Services
class DeliveryService:
    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        customer_repository: CustomerRepository,
        delivery_publisher: DeliveryPublisher,
        order_verification_service: OrderVerificationService,
    ):
        self.delivery_repository = delivery_repository
        self.customer_repository = customer_repository
        self.delivery_publisher = delivery_publisher
        self.order_verification_service = order_verification_service

    async def create_delivery(
        self,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
    ) -> DeliveryEntity:
        order_exists = await self.order_verification_service.verify_order(
            order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{order_id}' does not exist or is canceled"
            )

        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        delivery = DeliveryEntity(
            order_id=order_id,
            delivery_address=delivery_address,
            delivery_date=delivery_date,
            status=status,
            customer=existing_customer,
            address=address,
        )
        self.delivery_repository.save(delivery)
        return delivery

    def get_delivery_by_id(self, delivery_id: int) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")
        return delivery

    async def get_delivery_by_order_id(self, order_id: int) -> DeliveryEntity:
        order_exists = await self.order_verification_service.verify_order(
            order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{order_id}' does not exist or is canceled"
            )

        delivery = self.delivery_repository.find_by_order_id(order_id)
        if not delivery:
            raise EntityNotFound(
                f"Delivery with Order ID '{order_id}' not found"
            )
        return delivery

    async def update_delivery(
        self,
        delivery_id: int,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
    ) -> DeliveryEntity:
        order_exists = await self.order_verification_service.verify_order(
            order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{order_id}' does not exist or is canceled"
            )

        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        existing_customer = self.customer_repository.find_by_email(
            customer.email
        )
        if not existing_customer:
            self.customer_repository.save(customer)
            existing_customer = customer
        else:
            customer.id = existing_customer.id

        delivery.order_id = order_id
        delivery.delivery_address = delivery_address
        delivery.delivery_date = delivery_date
        delivery.status = status
        delivery.customer = existing_customer
        delivery.address = address

        self.delivery_repository.save(delivery)
        return delivery

    async def update_delivery_status(
        self, delivery_id: int, status: DeliveryStatus
    ) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        order_exists = await self.order_verification_service.verify_order(
            delivery.order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{delivery.order_id}' does not exist or is canceled"
            )

        delivery.update_status(status)
        self.delivery_repository.save(delivery)

        # Publish the delivery status update
        self.delivery_publisher.publish_delivery_update(
            delivery_id=delivery.id,
            order_id=delivery.order_id,
            status=delivery.status.value,
        )

        return delivery

    async def delete_delivery(self, delivery_id: int) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        order_exists = await self.order_verification_service.verify_order(
            delivery.order_id
        )
        if not order_exists:
            raise InvalidOperation(
                f"Order with ID '{delivery.order_id}' does not exist or is canceled"
            )

        self.delivery_repository.delete(delivery)
        return delivery

    def list_deliveries(self) -> List[DeliveryEntity]:
        return self.delivery_repository.list_all()


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
                pika.ConnectionParameters(host=self.rabbitmq_host)
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


# FastAPI Routes (Adapter)
@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_health_service(
    db: Session = Depends(get_db),
) -> HealthService:
    return HealthService(db, rabbitmq_host="rabbitmq")


def get_delivery_service(
    db: Session = Depends(get_db),
    delivery_publisher: DeliveryPublisher = Depends(
        lambda: DeliveryPublisher(pika.ConnectionParameters(host="rabbitmq"))
    ),
    order_verification_service: OrderVerificationService = Depends(
        OrderVerificationService
    ),
) -> DeliveryService:
    delivery_repository = SQLAlchemyDeliveryRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    return DeliveryService(
        delivery_repository,
        customer_repository,
        delivery_publisher,
        order_verification_service,
    )


# Pydantic Models for API
class AddressCreate(BaseModel):
    city: str
    state: str
    country: str
    zip_code: str


class CustomerCreate(BaseModel):
    name: str
    email: str


class DeliveryCreate(BaseModel):
    order_id: int
    delivery_address: str
    delivery_date: str
    status: DeliveryStatus
    address: AddressCreate
    customer: CustomerCreate


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus


class AddressResponse(BaseModel):
    id: int
    city: str
    state: str
    country: str
    zip_code: str

    class Config:
        orm_mode = True


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    delivery_address: str
    delivery_date: str
    status: DeliveryStatus
    address: AddressResponse
    customer: CustomerResponse

    class Config:
        orm_mode = True


@app.post("/deliveries/", response_model=DeliveryResponse)
async def create_delivery(
    delivery: DeliveryCreate,
    service: DeliveryService = Depends(get_delivery_service),
):
    customer_entity = CustomerEntity(
        name=delivery.customer.name, email=delivery.customer.email
    )
    address_entity = AddressEntity(
        city=delivery.address.city,
        state=delivery.address.state,
        country=delivery.address.country,
        zip_code=delivery.address.zip_code,
    )
    try:
        created_delivery = await service.create_delivery(
            order_id=delivery.order_id,
            delivery_address=delivery.delivery_address,
            delivery_date=delivery.delivery_date,
            status=delivery.status,
            customer=customer_entity,
            address=address_entity,
        )
        return serialize_delivery(created_delivery)
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/deliveries/", response_model=List[DeliveryResponse])
async def read_deliveries(
    service: DeliveryService = Depends(get_delivery_service),
):
    deliveries = service.list_deliveries()
    return [serialize_delivery(delivery) for delivery in deliveries]


@app.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
async def read_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        delivery = service.get_delivery_by_id(delivery_id)
        return serialize_delivery(delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/deliveries/by-order-id/{order_id}", response_model=DeliveryResponse)
async def read_delivery_by_order_id(
    order_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        delivery = await service.get_delivery_by_order_id(order_id)
        return serialize_delivery(delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/deliveries/{delivery_id}", response_model=DeliveryResponse)
async def update_delivery(
    delivery_id: int,
    delivery: DeliveryCreate,
    service: DeliveryService = Depends(get_delivery_service),
):
    customer_entity = CustomerEntity(
        name=delivery.customer.name, email=delivery.customer.email
    )
    address_entity = AddressEntity(
        city=delivery.address.city,
        state=delivery.address.state,
        country=delivery.address.country,
        zip_code=delivery.address.zip_code,
    )
    try:
        updated_delivery = await service.update_delivery(
            delivery_id=delivery_id,
            order_id=delivery.order_id,
            delivery_address=delivery.delivery_address,
            delivery_date=delivery.delivery_date,
            status=delivery.status,
            customer=customer_entity,
            address=address_entity,
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/deliveries/{delivery_id}/status", response_model=DeliveryResponse)
async def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    service: DeliveryService = Depends(get_delivery_service),
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, status_update.status
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/deliveries/{delivery_id}/delivered", response_model=DeliveryResponse
)
async def set_delivery_delivered(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, DeliveryStatus.DELIVERED
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put(
    "/deliveries/{delivery_id}/in-transit", response_model=DeliveryResponse
)
async def set_delivery_in_transit(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, DeliveryStatus.IN_TRANSIT
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/deliveries/{delivery_id}/cancel", response_model=DeliveryResponse)
async def cancel_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        updated_delivery = await service.update_delivery_status(
            delivery_id, DeliveryStatus.CANCELED
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/deliveries/{delivery_id}")
async def delete_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        await service.delete_delivery(delivery_id)
        return {"message": "Delivery deleted successfully"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health", tags=["Health"])
def health_check(health_service: HealthService = Depends(get_health_service)):
    return health_service.get_health_status()


# Serialization Functions
def serialize_delivery(delivery: DeliveryEntity) -> DeliveryResponse:
    return DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        status=delivery.status,
        customer=CustomerResponse(
            id=delivery.customer.id,
            name=delivery.customer.name,
            email=delivery.customer.email,
        ),
        address=AddressResponse(
            id=delivery.address.id,
            city=delivery.address.city,
            state=delivery.address.state,
            country=delivery.address.country,
            zip_code=delivery.address.zip_code,
        ),
    )
