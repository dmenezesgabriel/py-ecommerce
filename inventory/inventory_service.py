import json
import logging
import os
import threading
import time
from typing import List, Optional

import pika
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (Column, Float, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.sql import text

# Setup FastAPI
app = FastAPI()

# Database Configuration
DATABASE_URL = "sqlite:///./data/inventory.db"

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
class CategoryEntity:
    def __init__(self, name: str, id: Optional[int] = None):
        self.id = id
        self.name = name


class PriceEntity:
    def __init__(self, amount: float, id: Optional[int] = None):
        self.id = id
        self.amount = amount


class InventoryEntity:
    def __init__(self, quantity: int, id: Optional[int] = None):
        self.id = id
        self.quantity = quantity

    def set_quantity(self, amount: int):
        self.quantity = amount


class ProductEntity:
    def __init__(
        self,
        sku: str,
        name: str,
        category: CategoryEntity,
        price: PriceEntity,
        inventory: InventoryEntity,
        id: Optional[int] = None,
    ):
        self.id = id
        self.sku = sku
        self.name = name
        self.category = category
        self.price = price
        self.inventory = inventory

    def set_inventory(self, quantity: int):
        self.inventory.set_quantity(quantity)

    def set_price(self, amount: float):
        self.price.amount = amount

    def add_inventory(self, quantity: int):
        if quantity < 0:
            raise InvalidEntity("Quantity to add must be positive.")
        self.inventory.quantity += quantity

    def subtract_inventory(self, quantity: int):
        if quantity < 0:
            raise InvalidEntity("Quantity to subtract must be positive.")
        if self.inventory.quantity < quantity:
            raise InvalidEntity(
                f"Cannot subtract {quantity} items. Only {self.inventory.quantity} available."
            )
        self.inventory.quantity -= quantity


# Services
class ProductService:
    def __init__(self, product_repository, category_repository):
        self.product_repository = product_repository
        self.category_repository = category_repository

    def create_product(
        self,
        sku: str,
        name: str,
        category_name: str,
        price: float,
        quantity: int,
    ) -> ProductEntity:
        category = self.category_repository.find_by_name(category_name)
        if not category:
            category = CategoryEntity(name=category_name)
            self.category_repository.save(category)

        product = self.product_repository.find_by_sku(sku)
        if product:
            raise EntityAlreadyExists(
                f"Product with SKU '{sku}' already exists"
            )

        price_entity = PriceEntity(amount=price)
        inventory_entity = InventoryEntity(quantity=quantity)
        product = ProductEntity(
            sku, name, category, price_entity, inventory_entity
        )
        self.product_repository.save(product)
        return product

    def get_product_by_sku(self, sku: str) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")
        return product

    def update_product(
        self,
        sku: str,
        name: str,
        category_name: str,
        price: float,
        quantity: int,
    ) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        category = self.category_repository.find_by_name(category_name)
        if not category:
            category = CategoryEntity(name=category_name)
            self.category_repository.save(category)

        product.name = name
        product.category = category
        product.set_price(price)
        product.set_inventory(quantity)
        self.product_repository.save(product)
        return product

    def delete_product(self, sku: str) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        self.product_repository.delete(product)
        return product

    def list_products(self) -> List[ProductEntity]:
        return self.product_repository.list_all()

    def get_products_by_category(
        self, category_name: str
    ) -> List[ProductEntity]:
        category = self.category_repository.find_by_name(category_name)
        if not category:
            raise EntityNotFound(f"Category '{category_name}' not found")
        return self.product_repository.find_by_category(category)

    def add_inventory(self, sku: str, quantity: int) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        product.add_inventory(quantity)
        self.product_repository.save(product)
        return product

    def subtract_inventory(self, sku: str, quantity: int) -> ProductEntity:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        product.subtract_inventory(quantity)
        self.product_repository.save(product)
        return product

    def create_category(self, name: str) -> CategoryEntity:
        category = self.category_repository.find_by_name(name)
        if category:
            raise EntityAlreadyExists(
                f"Category with name '{name}' already exists"
            )
        category = CategoryEntity(name=name)
        self.category_repository.save(category)
        return category

    def list_categories(self) -> List[CategoryEntity]:
        return self.category_repository.list_all()


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


# Ports (Interfaces)
class ProductRepository:
    def save(self, product: ProductEntity):
        raise NotImplementedError

    def find_by_sku(self, sku: str) -> Optional[ProductEntity]:
        raise NotImplementedError

    def delete(self, product: ProductEntity):
        raise NotImplementedError

    def list_all(self) -> List[ProductEntity]:
        raise NotImplementedError

    def find_by_category(
        self, category: CategoryEntity
    ) -> List[ProductEntity]:
        raise NotImplementedError


class CategoryRepository:
    def save(self, category: CategoryEntity):
        raise NotImplementedError

    def find_by_name(self, name: str) -> Optional[CategoryEntity]:
        raise NotImplementedError

    def list_all(self) -> List[CategoryEntity]:
        raise NotImplementedError


# Adapters
# SQLAlchemy Mappers and Repositories
class CategoryModel(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    products = relationship("ProductModel", back_populates="category")


class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("CategoryModel", back_populates="products")
    price = relationship("PriceModel", uselist=False, back_populates="product")
    inventory = relationship(
        "InventoryModel", uselist=False, back_populates="product"
    )


class PriceModel(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    amount = Column(Float)
    product = relationship("ProductModel", back_populates="price")


class InventoryModel(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    product = relationship("ProductModel", back_populates="inventory")


class SQLAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, product: ProductEntity):
        category_model = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == product.category.name)
            .first()
        )
        if not category_model:
            category_model = CategoryModel(name=product.category.name)
            self.db.add(category_model)
            self.db.commit()
            self.db.refresh(category_model)

        if product.id:
            db_product = (
                self.db.query(ProductModel)
                .filter(ProductModel.id == product.id)
                .first()
            )
        else:
            db_product = ProductModel(
                sku=product.sku,
                name=product.name,
                category_id=category_model.id,
            )
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)

        db_product.price = PriceModel(
            product_id=db_product.id, amount=product.price.amount
        )
        db_product.inventory = InventoryModel(
            product_id=db_product.id, quantity=product.inventory.quantity
        )

        self.db.add(db_product.price)
        self.db.add(db_product.inventory)
        self.db.commit()
        self.db.refresh(db_product)

    def find_by_sku(self, sku: str) -> Optional[ProductEntity]:
        db_product = (
            self.db.query(ProductModel).filter(ProductModel.sku == sku).first()
        )
        if db_product:
            category = (
                self.db.query(CategoryModel)
                .filter(CategoryModel.id == db_product.category_id)
                .first()
            )
            return ProductEntity(
                id=db_product.id,
                sku=db_product.sku,
                name=db_product.name,
                category=CategoryEntity(id=category.id, name=category.name),
                price=PriceEntity(
                    id=db_product.price.id, amount=db_product.price.amount
                ),
                inventory=InventoryEntity(
                    id=db_product.inventory.id,
                    quantity=db_product.inventory.quantity,
                ),
            )
        return None

    def delete(self, product: ProductEntity):
        db_product = (
            self.db.query(ProductModel)
            .filter(ProductModel.sku == product.sku)
            .first()
        )
        if db_product:
            db_price = (
                self.db.query(PriceModel)
                .filter(PriceModel.product_id == db_product.id)
                .first()
            )
            db_inventory = (
                self.db.query(InventoryModel)
                .filter(InventoryModel.product_id == db_product.id)
                .first()
            )

            self.db.delete(db_inventory)
            self.db.delete(db_price)
            self.db.delete(db_product)
            self.db.commit()

    def list_all(self) -> List[ProductEntity]:
        db_products = self.db.query(ProductModel).all()
        return [
            ProductEntity(
                id=db_product.id,
                sku=db_product.sku,
                name=db_product.name,
                category=CategoryEntity(
                    id=db_product.category.id, name=db_product.category.name
                ),
                price=PriceEntity(
                    id=db_product.price.id, amount=db_product.price.amount
                ),
                inventory=InventoryEntity(
                    id=db_product.inventory.id,
                    quantity=db_product.inventory.quantity,
                ),
            )
            for db_product in db_products
        ]

    def find_by_category(
        self, category: CategoryEntity
    ) -> List[ProductEntity]:
        db_category = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == category.name)
            .first()
        )
        if db_category:
            db_products = (
                self.db.query(ProductModel)
                .filter(ProductModel.category_id == db_category.id)
                .all()
            )
            return [
                ProductEntity(
                    id=db_product.id,
                    sku=db_product.sku,
                    name=db_product.name,
                    category=CategoryEntity(
                        id=db_category.id, name=db_category.name
                    ),
                    price=PriceEntity(
                        id=db_product.price.id, amount=db_product.price.amount
                    ),
                    inventory=InventoryEntity(
                        id=db_product.inventory.id,
                        quantity=db_product.inventory.quantity,
                    ),
                )
                for db_product in db_products
            ]
        return []


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, category: CategoryEntity):
        db_category = CategoryModel(name=category.name)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        category.id = db_category.id

    def find_by_name(self, name: str) -> Optional[CategoryEntity]:
        db_category = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == name)
            .first()
        )
        if db_category:
            return CategoryEntity(id=db_category.id, name=db_category.name)
        return None

    def list_all(self) -> List[CategoryEntity]:
        db_categories = self.db.query(CategoryModel).all()
        return [
            CategoryEntity(id=db_category.id, name=db_category.name)
            for db_category in db_categories
        ]


# Subscriber Adapter using Pika
class InventorySubscriber:
    def __init__(
        self,
        product_service: ProductService,
        max_retries: int = 5,
        delay: int = 5,
    ):
        self.product_service = product_service
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
            exchange="inventory_exchange", exchange_type="direct", durable=True
        )
        self.channel.queue_declare(queue="inventory_queue", durable=True)
        self.channel.queue_bind(
            exchange="inventory_exchange",
            queue="inventory_queue",
            routing_key="inventory_queue",
        )

        self.channel.basic_consume(
            queue="inventory_queue",
            on_message_callback=self.on_message,
            auto_ack=False,
        )

        logger.info("Starting to consume messages from inventory_queue.")
        self.channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        logger.info(f"Received message from inventory_queue: {body}")
        try:
            data = json.loads(body.decode("utf-8"))
            sku = data.get("sku")
            action = data.get("action")
            quantity = data.get("quantity")

            if action == "add":
                self.product_service.add_inventory(sku, quantity)
                logger.info(f"Added {quantity} to SKU: {sku}.")
            elif action == "subtract":
                self.product_service.subtract_inventory(sku, quantity)
                logger.info(f"Subtracted {quantity} from SKU: {sku}.")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)


# FastAPI Routes (Adapter)
@app.on_event("startup")
def on_startup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    product_repository = SQLAlchemyProductRepository(db)
    category_repository = SQLAlchemyCategoryRepository(db)
    product_service = ProductService(product_repository, category_repository)

    inventory_subscriber = InventorySubscriber(product_service)
    threading.Thread(target=inventory_subscriber.start_consuming).start()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_health_service(db: Session = Depends(get_db)) -> HealthService:
    return HealthService(db, rabbitmq_host="rabbitmq")


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repository = SQLAlchemyProductRepository(db)
    category_repository = SQLAlchemyCategoryRepository(db)
    return ProductService(product_repository, category_repository)


# Pydantic Models for API
class ProductCreate(BaseModel):
    sku: str
    name: str
    category_name: str
    price: float
    quantity: int


class ProductUpdate(BaseModel):
    name: str
    category_name: str
    price: float
    quantity: int


class ProductResponse(BaseModel):
    sku: str
    name: str
    category_name: str
    price: float
    quantity: int


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str


class InventoryUpdate(BaseModel):
    quantity: int


@app.post("/products/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    try:
        created_product = service.create_product(
            sku=product.sku,
            name=product.name,
            category_name=product.category_name,
            price=product.price,
            quantity=product.quantity,
        )
        return serialize_product(created_product)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/products/", response_model=List[ProductResponse])
def read_products(service: ProductService = Depends(get_product_service)):
    products = service.list_products()
    return [serialize_product(product) for product in products]


@app.get("/products/{sku}", response_model=ProductResponse)
def read_product(
    sku: str, service: ProductService = Depends(get_product_service)
):
    try:
        product = service.get_product_by_sku(sku)
        return serialize_product(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/products/{sku}", response_model=ProductResponse)
def update_product(
    sku: str,
    product: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        updated_product = service.update_product(
            sku=sku,
            name=product.name,
            category_name=product.category_name,
            price=product.price,
            quantity=product.quantity,
        )
        return serialize_product(updated_product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/products/{sku}", response_model=ProductResponse)
def delete_product(
    sku: str, service: ProductService = Depends(get_product_service)
):
    try:
        deleted_product = service.delete_product(sku)
        return serialize_product(deleted_product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/products/by-category/{category_name}",
    response_model=List[ProductResponse],
)
def get_products_by_category(
    category_name: str, service: ProductService = Depends(get_product_service)
):
    try:
        products = service.get_products_by_category(category_name)
        return [serialize_product(product) for product in products]
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/inventory/{sku}/add", response_model=ProductResponse)
def add_inventory(
    sku: str,
    inventory_update: InventoryUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        product = service.add_inventory(sku, inventory_update.quantity)
        return serialize_product(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/inventory/{sku}/subtract", response_model=ProductResponse)
def subtract_inventory(
    sku: str,
    inventory_update: InventoryUpdate,
    service: ProductService = Depends(get_product_service),
):
    try:
        product = service.subtract_inventory(sku, inventory_update.quantity)
        return serialize_product(product)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidEntity as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/categories/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    service: ProductService = Depends(get_product_service),
):
    try:
        created_category = service.create_category(name=category.name)
        return serialize_category(created_category)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/categories/", response_model=List[CategoryResponse])
def list_categories(service: ProductService = Depends(get_product_service)):
    categories = service.list_categories()
    return [serialize_category(category) for category in categories]


# Serialization Functions
def serialize_product(product: ProductEntity) -> ProductResponse:
    return ProductResponse(
        sku=product.sku,
        name=product.name,
        category_name=product.category.name,
        price=product.price.amount,
        quantity=product.inventory.quantity,
    )


def serialize_category(category: CategoryEntity) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
    )


@app.get("/health", tags=["Health"])
def health_check(service: HealthService = Depends(get_health_service)):
    return service.get_health_status()
