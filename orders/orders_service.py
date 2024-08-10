import os
import uuid
from enum import Enum as PyEnum
from typing import List, Optional

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

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
        else:
            db_order = OrderModel(
                order_number=order.order_number,
                customer_id=customer_model.id,
                status=order.status,
            )
            self.db.add(db_order)
            self.db.commit()
            self.db.refresh(db_order)

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


# Services
class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        customer_repository: CustomerRepository,
    ):
        self.order_repository = order_repository
        self.customer_repository = customer_repository

    async def check_inventory(
        self, sku: str, quantity: int, session: aiohttp.ClientSession
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
            return product["price"]

    async def adjust_inventory(
        self,
        sku: str,
        quantity: int,
        session: aiohttp.ClientSession,
        action: str,
    ):
        async with session.post(
            f"http://inventory_service:8001/inventory/{sku}/{action}",
            json={"quantity": quantity},
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to {action} inventory",
                )

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

        async with aiohttp.ClientSession() as session:
            try:
                total_amount = 0.0
                for item in order_items:
                    product_price = await self.check_inventory(
                        item.product_sku, item.quantity, session
                    )
                    await self.adjust_inventory(
                        item.product_sku, item.quantity, session, "subtract"
                    )
                    total_amount += product_price * item.quantity

                self.order_repository.save(order)
                return order, total_amount

            except Exception as e:
                # Rollback inventory if there's any error
                for item in order_items:
                    await self.adjust_inventory(
                        item.product_sku, item.quantity, session, "add"
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

        # Inventory adjustments to revert if needed
        inventory_changes = []

        async with aiohttp.ClientSession() as session:
            try:
                # Get current order items to compare
                current_order_items = {
                    item.product_sku: item.quantity
                    for item in order.order_items
                }

                total_amount = 0.0
                for item in order_items:
                    if item.product_sku in current_order_items:
                        old_quantity = current_order_items[item.product_sku]
                        if item.quantity > old_quantity:
                            diff = item.quantity - old_quantity
                            await self.adjust_inventory(
                                item.product_sku, diff, session, "subtract"
                            )
                            inventory_changes.append((item.product_sku, diff))
                        elif item.quantity < old_quantity:
                            diff = old_quantity - item.quantity
                            await self.adjust_inventory(
                                item.product_sku, diff, session, "add"
                            )
                            inventory_changes.append((item.product_sku, -diff))
                    else:
                        await self.check_inventory(
                            item.product_sku, item.quantity, session
                        )
                        await self.adjust_inventory(
                            item.product_sku,
                            item.quantity,
                            session,
                            "subtract",
                        )
                        inventory_changes.append(
                            (item.product_sku, item.quantity)
                        )

                    product_price = await self.check_inventory(
                        item.product_sku, item.quantity, session
                    )
                    total_amount += product_price * item.quantity

                order.customer = existing_customer
                order.order_items = order_items
                self.order_repository.save(order)
                return order, total_amount

            except Exception as e:
                # Rollback inventory if there's any error
                for sku, quantity in inventory_changes:
                    action = "add" if quantity > 0 else "subtract"
                    await self.adjust_inventory(
                        sku, abs(quantity), session, action
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

    def delete_order(self, order_id: int) -> OrderEntity:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise EntityNotFound(f"Order with ID '{order_id}' not found")

        self.order_repository.delete(order)
        return order

    def list_orders(self) -> List[OrderEntity]:
        return self.order_repository.list_all()


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


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    order_repository = SQLAlchemyOrderRepository(db)
    customer_repository = SQLAlchemyCustomerRepository(db)
    return OrderService(order_repository, customer_repository)


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
    return [
        serialize_order(order, 0) for order in orders
    ]  # total_amount not available in listing


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int, service: OrderService = Depends(get_order_service)
):
    try:
        order = service.get_order_by_id(order_id)
        total_amount = await calculate_order_total(
            order
        )  # Helper function to calculate total amount
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
        total_amount = await calculate_order_total(
            order
        )  # Helper function to calculate total amount
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
        total_amount = await calculate_order_total(
            updated_order
        )  # Helper function to calculate total amount
        return serialize_order(updated_order, total_amount)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


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


async def calculate_order_total(order: OrderEntity) -> float:
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
