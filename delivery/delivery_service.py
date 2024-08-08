import os
from enum import Enum
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./data/deliveries.db"

# Ensure the data directory exists
if not os.path.exists("./data"):
    os.makedirs("./data")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELED = "canceled"


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    delivery = relationship("Delivery", back_populates="address")


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    delivery_address = Column(String)
    delivery_date = Column(String)
    status = Column(SQLAEnum(DeliveryStatus), default=DeliveryStatus.PENDING)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    address = relationship("Address", uselist=False, back_populates="delivery")
    customer = relationship("Customer")


# Pydantic models for Delivery
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


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@app.post("/deliveries/", response_model=DeliveryResponse)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    # Check if the customer exists
    db_customer = (
        db.query(Customer)
        .filter(Customer.email == delivery.customer.email)
        .first()
    )
    if not db_customer:
        db_customer = Customer(
            name=delivery.customer.name, email=delivery.customer.email
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)

    db_delivery = Delivery(
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        status=delivery.status,
        customer_id=db_customer.id,
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)

    db_address = Address(
        delivery_id=db_delivery.id,
        city=delivery.address.city,
        state=delivery.address.state,
        country=delivery.address.country,
        zip_code=delivery.address.zip_code,
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    db_delivery.address = db_address
    db_delivery.customer = db_customer
    return db_delivery


@app.get("/deliveries/", response_model=List[DeliveryResponse])
def read_deliveries(db: Session = Depends(get_db)):
    deliveries = db.query(Delivery).all()
    return deliveries


@app.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def read_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@app.get("/deliveries/by-order-id/{order_id}", response_model=DeliveryResponse)
def read_delivery_by_order_id(order_id: int, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@app.put("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int, delivery: DeliveryCreate, db: Session = Depends(get_db)
):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Update customer information
    db_customer = (
        db.query(Customer)
        .filter(Customer.email == delivery.customer.email)
        .first()
    )
    if not db_customer:
        db_customer = Customer(
            name=delivery.customer.name, email=delivery.customer.email
        )
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
    db_delivery.customer_id = db_customer.id

    db_delivery.order_id = delivery.order_id
    db_delivery.delivery_address = delivery.delivery_address
    db_delivery.delivery_date = delivery.delivery_date
    db_delivery.status = delivery.status
    db.commit()
    db.refresh(db_delivery)

    db_address = (
        db.query(Address).filter(Address.delivery_id == delivery_id).first()
    )
    db_address.city = delivery.address.city
    db_address.state = delivery.address.state
    db_address.country = delivery.address.country
    db_address.zip_code = delivery.address.zip_code
    db.commit()
    db.refresh(db_address)

    db_delivery.address = db_address
    db_delivery.customer = db_customer
    return db_delivery


@app.put("/deliveries/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    db_delivery.status = status_update.status
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


@app.delete("/deliveries/{delivery_id}")
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(db_delivery)
    db.commit()
    return {"message": "Delivery deleted successfully"}
