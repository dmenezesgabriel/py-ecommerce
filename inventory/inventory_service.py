import os
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

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


# Custom Exceptions
class EntityNotFound(Exception):
    pass


class EntityAlreadyExists(Exception):
    pass


class InvalidEntity(Exception):
    pass


# Entities
class Category:
    def __init__(self, name: str, id: Optional[int] = None):
        self.id = id
        self.name = name


class Product:
    def __init__(
        self,
        sku: str,
        name: str,
        category: Category,
        price: float,
        quantity: int,
        id: Optional[int] = None,
    ):
        self.id = id
        self.sku = sku
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity

    def update_inventory(self, quantity: int):
        if quantity < 0 and self.quantity + quantity < 0:
            raise InvalidEntity("Not enough inventory to subtract")
        self.quantity += quantity

    def set_price(self, price: float):
        self.price = price


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
    ) -> Product:
        category = self.category_repository.find_by_name(category_name)
        if not category:
            category = Category(name=category_name)
            self.category_repository.save(category)

        product = self.product_repository.find_by_sku(sku)
        if product:
            raise EntityAlreadyExists(
                f"Product with SKU '{sku}' already exists"
            )

        product = Product(sku, name, category, price, quantity)
        self.product_repository.save(product)
        return product

    def get_product_by_sku(self, sku: str) -> Product:
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
    ) -> Product:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        category = self.category_repository.find_by_name(category_name)
        if not category:
            category = Category(name=category_name)
            self.category_repository.save(category)

        product.name = name
        product.category = category
        product.set_price(price)
        product.update_inventory(quantity)
        self.product_repository.save(product)
        return product

    def delete_product(self, sku: str) -> Product:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        self.product_repository.delete(product)
        return product

    def list_products(self) -> List[Product]:
        return self.product_repository.list_all()

    def get_products_by_category(self, category_name: str) -> List[Product]:
        category = self.category_repository.find_by_name(category_name)
        if not category:
            raise EntityNotFound(f"Category '{category_name}' not found")
        return self.product_repository.find_by_category(category)

    def add_inventory(self, sku: str, quantity: int) -> Product:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        product.update_inventory(quantity)
        self.product_repository.save(product)
        return product

    def subtract_inventory(self, sku: str, quantity: int) -> Product:
        product = self.product_repository.find_by_sku(sku)
        if not product:
            raise EntityNotFound(f"Product with SKU '{sku}' not found")

        product.update_inventory(-quantity)
        self.product_repository.save(product)
        return product

    def create_category(self, name: str) -> Category:
        category = self.category_repository.find_by_name(name)
        if category:
            raise EntityAlreadyExists(
                f"Category with name '{name}' already exists"
            )
        category = Category(name=name)
        self.category_repository.save(category)
        return category

    def list_categories(self) -> List[Category]:
        return self.category_repository.list_all()


# Ports (Interfaces)
class ProductRepository:
    def save(self, product: Product):
        raise NotImplementedError

    def find_by_sku(self, sku: str) -> Optional[Product]:
        raise NotImplementedError

    def delete(self, product: Product):
        raise NotImplementedError

    def list_all(self) -> List[Product]:
        raise NotImplementedError

    def find_by_category(self, category: Category) -> List[Product]:
        raise NotImplementedError


class CategoryRepository:
    def save(self, category: Category):
        raise NotImplementedError

    def find_by_name(self, name: str) -> Optional[Category]:
        raise NotImplementedError

    def list_all(self) -> List[Category]:
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

    def save(self, product: Product):
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
        db_product.name = product.name
        db_product.sku = product.sku
        db_product.category_id = category_model.id
        db_product.price = PriceModel(
            product_id=db_product.id, amount=product.price
        )
        db_product.inventory = InventoryModel(
            product_id=db_product.id, quantity=product.quantity
        )

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

    def find_by_sku(self, sku: str) -> Optional[Product]:
        db_product = (
            self.db.query(ProductModel).filter(ProductModel.sku == sku).first()
        )
        if db_product:
            category = (
                self.db.query(CategoryModel)
                .filter(CategoryModel.id == db_product.category_id)
                .first()
            )
            return Product(
                id=db_product.id,
                sku=db_product.sku,
                name=db_product.name,
                category=Category(id=category.id, name=category.name),
                price=db_product.price.amount,
                quantity=db_product.inventory.quantity,
            )
        return None

    def delete(self, product: Product):
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

    def list_all(self) -> List[Product]:
        db_products = self.db.query(ProductModel).all()
        return [
            Product(
                id=db_product.id,
                sku=db_product.sku,
                name=db_product.name,
                category=Category(
                    id=db_product.category.id, name=db_product.category.name
                ),
                price=db_product.price.amount,
                quantity=db_product.inventory.quantity,
            )
            for db_product in db_products
        ]

    def find_by_category(self, category: Category) -> List[Product]:
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
                Product(
                    id=db_product.id,
                    sku=db_product.sku,
                    name=db_product.name,
                    category=Category(
                        id=db_category.id, name=db_category.name
                    ),
                    price=db_product.price.amount,
                    quantity=db_product.inventory.quantity,
                )
                for db_product in db_products
            ]
        return []


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, category: Category):
        db_category = CategoryModel(name=category.name)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)

    def find_by_name(self, name: str) -> Optional[Category]:
        db_category = (
            self.db.query(CategoryModel)
            .filter(CategoryModel.name == name)
            .first()
        )
        if db_category:
            return Category(id=db_category.id, name=db_category.name)
        return None

    def list_all(self) -> List[Category]:
        db_categories = self.db.query(CategoryModel).all()
        return [
            Category(id=db_category.id, name=db_category.name)
            for db_category in db_categories
        ]


# FastAPI Routes (Adapter)
@app.on_event("startup")
def on_startup():
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    sku: str
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
def serialize_product(product: Product) -> ProductResponse:
    return ProductResponse(
        sku=product.sku,
        name=product.name,
        category_name=product.category.name,
        price=product.price,
        quantity=product.quantity,
    )


def serialize_category(category: Category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
    )
