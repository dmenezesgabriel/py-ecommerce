import os
import uuid
from enum import Enum as PyEnum
from typing import List

import aiohttp  # For making asynchronous HTTP requests
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


# Enum for Order Status
class OrderStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"


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
    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(
        String, unique=True, index=True, default=lambda: str(uuid.uuid4())
    )
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
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
    order_number: str
    customer: CustomerResponse
    order_items: List[OrderItemResponse]
    total_amount: float  # Add total_amount field
    status: OrderStatus  # Add status field


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


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


def serialize_order(order: Order, total_amount: float) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
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
        total_amount=total_amount,  # Include total_amount
        status=order.status,  # Include status
    )


async def check_inventory(
    sku: str, quantity: int, session: aiohttp.ClientSession
):
    async with session.get(
        f"http://inventory_service:8001/products/{sku}"
    ) as response:
        if response.status != 200:
            raise HTTPException(
                status_code=404, detail=f"Product {sku} not found"
            )
        product = await response.json()
        if product["quantity"] < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough inventory for product {sku}",
            )


@app.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    async with aiohttp.ClientSession() as session:
        try:
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

            total_amount = 0.0
            for item in order.order_items:
                # Check inventory before creating order
                await check_inventory(item.product_sku, item.quantity, session)

                # Subtract from inventory
                async with session.post(
                    f"http://inventory_service:8001/inventory/{item.product_sku}/subtract",
                    json={"quantity": item.quantity},
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=400,
                            detail="Failed to update inventory",
                        )

                db_order_item = OrderItem(
                    order_id=db_order.id,
                    product_sku=item.product_sku,
                    quantity=item.quantity,
                )
                db.add(db_order_item)
                async with session.get(
                    f"http://inventory_service:8001/products/{item.product_sku}"
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Product {item.product_sku} not found",
                        )
                    product = await response.json()
                    product_price = product["price"]
                    total_amount += product_price * item.quantity

            db.commit()
            return serialize_order(db_order, total_amount)

        except Exception as e:
            # Rollback inventory if there's any error
            db.rollback()
            # Rollback inventory changes made before the failure
            for item in order.order_items:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        f"http://inventory_service:8001/inventory/{item.product_sku}/add",
                        json={"quantity": item.quantity},
                    )
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/", response_model=List[OrderResponse])
async def read_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    result = []
    async with aiohttp.ClientSession() as session:
        for order in orders:
            order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.id)
                .all()
            )
            total_amount = 0.0
            for item in order_items:
                async with session.get(
                    f"http://inventory_service:8001/products/{item.product_sku}"
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Product {item.product_sku} not found",
                        )
                    product = await response.json()
                    product_price = product["price"]
                    total_amount += product_price * item.quantity
            result.append(serialize_order(order, total_amount))
    return result


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_items = (
        db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    )
    total_amount = 0.0
    async with aiohttp.ClientSession() as session:
        for item in order_items:
            async with session.get(
                f"http://inventory_service:8001/products/{item.product_sku}"
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_sku} not found",
                    )
                product = await response.json()
                product_price = product["price"]
                total_amount += product_price * item.quantity
    return serialize_order(order, total_amount)


@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int, order: OrderCreate, db: Session = Depends(get_db)
):
    async with aiohttp.ClientSession() as session:
        # Track inventory changes to revert if needed
        inventory_changes = []

        try:
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

            # Retrieve existing order items to compare with new ones
            existing_order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order_id)
                .all()
            )
            existing_order_items_dict = {
                item.product_sku: item.quantity
                for item in existing_order_items
            }

            # Remove old order items
            db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

            total_amount = 0.0
            for item in order.order_items:
                # Check inventory before updating order
                await check_inventory(item.product_sku, item.quantity, session)

                if item.product_sku in existing_order_items_dict:
                    old_quantity = existing_order_items_dict[item.product_sku]
                    if item.quantity > old_quantity:
                        # If new quantity is greater, subtract the difference
                        diff = item.quantity - old_quantity
                        async with session.post(
                            f"http://inventory_service:8001/inventory/{item.product_sku}/subtract",
                            json={"quantity": diff},
                        ) as response:
                            if response.status != 200:
                                raise HTTPException(
                                    status_code=400,
                                    detail="Failed to update inventory",
                                )
                        inventory_changes.append((item.product_sku, diff))
                    elif item.quantity < old_quantity:
                        # If new quantity is less, add back the difference
                        diff = old_quantity - item.quantity
                        async with session.post(
                            f"http://inventory_service:8001/inventory/{item.product_sku}/add",
                            json={"quantity": diff},
                        ) as response:
                            if response.status != 200:
                                raise HTTPException(
                                    status_code=400,
                                    detail="Failed to update inventory",
                                )
                        inventory_changes.append((item.product_sku, -diff))
                else:
                    # New item, subtract its quantity
                    async with session.post(
                        f"http://inventory_service:8001/inventory/{item.product_sku}/subtract",
                        json={"quantity": item.quantity},
                    ) as response:
                        if response.status != 200:
                            raise HTTPException(
                                status_code=400,
                                detail="Failed to update inventory",
                            )
                    inventory_changes.append((item.product_sku, item.quantity))

                db_order_item = OrderItem(
                    order_id=order_id,
                    product_sku=item.product_sku,
                    quantity=item.quantity,
                )
                db.add(db_order_item)

                async with session.get(
                    f"http://inventory_service:8001/products/{item.product_sku}"
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Product {item.product_sku} not found",
                        )
                    product = await response.json()
                    product_price = product["price"]
                    total_amount += product_price * item.quantity

            db.commit()
            return serialize_order(db_order, total_amount)

        except Exception as e:
            # Rollback inventory if there's any error
            db.rollback()
            # Revert inventory changes made during the operation
            for sku, quantity in inventory_changes:
                async with aiohttp.ClientSession() as session:
                    if quantity > 0:
                        await session.post(
                            f"http://inventory_service:8001/inventory/{sku}/add",
                            json={"quantity": quantity},
                        )
                    else:
                        await session.post(
                            f"http://inventory_service:8001/inventory/{sku}/subtract",
                            json={"quantity": -quantity},
                        )
            raise HTTPException(status_code=500, detail=str(e))


@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()


@app.get("/customers/", response_model=List[CustomerResponse])
def read_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/customers/", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(name=customer.name, email=customer.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)
):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db_customer.name = customer.name
    db_customer.email = customer.email
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()


@app.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_update.status
    db.commit()
    db.refresh(order)

    order_items = (
        db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    )
    total_amount = 0.0
    async with aiohttp.ClientSession() as session:
        for item in order_items:
            async with session.get(
                f"http://inventory_service:8001/products/{item.product_sku}"
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item.product_sku} not found",
                    )
                product = await response.json()
                product_price = product["price"]
                total_amount += product_price * item.quantity

    return serialize_order(order, total_amount)
