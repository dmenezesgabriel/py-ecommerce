import os
from enum import Enum
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

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


# Custom Exceptions
class EntityNotFound(Exception):
    pass


class EntityAlreadyExists(Exception):
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


# Services
class DeliveryService:
    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        customer_repository: CustomerRepository,
    ):
        self.delivery_repository = delivery_repository
        self.customer_repository = customer_repository

    def create_delivery(
        self,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
    ) -> DeliveryEntity:
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

    def get_delivery_by_order_id(self, order_id: int) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_order_id(order_id)
        if not delivery:
            raise EntityNotFound(
                f"Delivery with Order ID '{order_id}' not found"
            )
        return delivery

    def update_delivery(
        self,
        delivery_id: int,
        order_id: int,
        delivery_address: str,
        delivery_date: str,
        status: DeliveryStatus,
        customer: CustomerEntity,
        address: AddressEntity,
    ) -> DeliveryEntity:
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

    def update_delivery_status(
        self, delivery_id: int, status: DeliveryStatus
    ) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        delivery.update_status(status)
        self.delivery_repository.save(delivery)
        return delivery

    def delete_delivery(self, delivery_id: int) -> DeliveryEntity:
        delivery = self.delivery_repository.find_by_id(delivery_id)
        if not delivery:
            raise EntityNotFound(f"Delivery with ID '{delivery_id}' not found")

        self.delivery_repository.delete(delivery)
        return delivery

    def list_deliveries(self) -> List[DeliveryEntity]:
        return self.delivery_repository.list_all()


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


def get_delivery_service(db: Session = Depends(get_db)) -> DeliveryService:
    delivery_repository = SQLAlchemyDeliveryRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    return DeliveryService(delivery_repository, customer_repository)


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
def create_delivery(
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
    created_delivery = service.create_delivery(
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        status=delivery.status,
        customer=customer_entity,
        address=address_entity,
    )
    return serialize_delivery(created_delivery)


@app.get("/deliveries/", response_model=List[DeliveryResponse])
def read_deliveries(service: DeliveryService = Depends(get_delivery_service)):
    deliveries = service.list_deliveries()
    return [serialize_delivery(delivery) for delivery in deliveries]


@app.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def read_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        delivery = service.get_delivery_by_id(delivery_id)
        return serialize_delivery(delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/deliveries/by-order-id/{order_id}", response_model=DeliveryResponse)
def read_delivery_by_order_id(
    order_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        delivery = service.get_delivery_by_order_id(order_id)
        return serialize_delivery(delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
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
        updated_delivery = service.update_delivery(
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


@app.put("/deliveries/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    service: DeliveryService = Depends(get_delivery_service),
):
    try:
        updated_delivery = service.update_delivery_status(
            delivery_id, status_update.status
        )
        return serialize_delivery(updated_delivery)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/deliveries/{delivery_id}")
def delete_delivery(
    delivery_id: int, service: DeliveryService = Depends(get_delivery_service)
):
    try:
        service.delete_delivery(delivery_id)
        return {"message": "Delivery deleted successfully"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


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
