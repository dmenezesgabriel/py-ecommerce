import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
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


# SQLAlchemy Models
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


Customer.orders = relationship(
    "Order", order_by=Order.id, back_populates="customer"
)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_sku = Column(String, index=True)
    quantity = Column(Integer)
    order = relationship("Order", back_populates="order_items")


# Pydantic Models
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


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str


class OrderResponse(BaseModel):
    id: int
    customer: CustomerResponse
    order_items: List[OrderItemResponse]


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


def serialize_order(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        customer=CustomerResponse(
            id=order.customer.id,
            name=order.customer.name,
            email=order.customer.email,
        ),
        order_items=[
            OrderItemResponse(
                product_sku=item.product_sku, quantity=item.quantity
            )
            for item in order.order_items
        ],
    )


@app.post("/orders/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Check if the customer already exists
    customer = (
        db.query(Customer)
        .filter(Customer.email == order.customer.email)
        .first()
    )
    if not customer:
        customer = Customer(
            name=order.customer.name, email=order.customer.email
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    db_order = Order(customer_id=customer.id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.order_items:
        db_order_item = OrderItem(
            order_id=db_order.id,
            product_sku=item.product_sku,
            quantity=item.quantity,
        )
        db.add(db_order_item)
    db.commit()

    return serialize_order(db_order)


@app.get("/orders/", response_model=List[OrderResponse])
def read_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return [serialize_order(order) for order in orders]


@app.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(order)


@app.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int, order: OrderCreate, db: Session = Depends(get_db)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update customer information
    customer = (
        db.query(Customer)
        .filter(Customer.email == order.customer.email)
        .first()
    )
    if not customer:
        customer = Customer(
            name=order.customer.name, email=order.customer.email
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    db_order.customer_id = customer.id

    # Update order items
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    for item in order.order_items:
        db_order_item = OrderItem(
            order_id=order_id,
            product_sku=item.product_sku,
            quantity=item.quantity,
        )
        db.add(db_order_item)
    db.commit()

    return serialize_order(db_order)


@app.delete("/orders/{order_id}", response_model=OrderResponse)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(db_order)
    db.commit()

    return serialize_order(db_order)
