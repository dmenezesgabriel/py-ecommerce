import os

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

app = FastAPI()

DATABASE_URL = "sqlite:///./data/inventory.db"

# Ensure the data directory exists
if not os.path.exists("/app/data"):
    os.makedirs("/app/data")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy Models
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    price = relationship("Price", uselist=False, back_populates="product")
    inventory = relationship(
        "Inventory", uselist=False, back_populates="product"
    )


class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    amount = Column(Float)
    product = relationship("Product", back_populates="price")


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    product = relationship("Product", back_populates="inventory")


Category.products = relationship(
    "Product", order_by=Product.id, back_populates="category"
)


# Pydantic Models
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


def serialize_product(product: Product) -> ProductResponse:
    return ProductResponse(
        sku=product.sku,
        name=product.name,
        category_name=product.category.name,
        price=product.price.amount,
        quantity=product.inventory.quantity,
    )


@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    category = (
        db.query(Category)
        .filter(Category.name == product.category_name)
        .first()
    )
    if not category:
        category = Category(name=product.category_name)
        db.add(category)
        db.commit()
        db.refresh(category)

    db_product = db.query(Product).filter(Product.sku == product.sku).first()
    if db_product:
        raise HTTPException(
            status_code=400, detail="Product with this SKU already exists"
        )

    db_product = Product(
        sku=product.sku, name=product.name, category_id=category.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    db_price = Price(product_id=db_product.id, amount=product.price)
    db.add(db_price)
    db.commit()
    db.refresh(db_price)

    db_inventory = Inventory(
        product_id=db_product.id, quantity=product.quantity
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)

    return serialize_product(db_product)


@app.get("/products/", response_model=list[ProductResponse])
def read_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [serialize_product(product) for product in products]


@app.get("/products/{sku}", response_model=ProductResponse)
def read_product(sku: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_product(product)


@app.put("/products/{sku}", response_model=ProductResponse)
def update_product(
    sku: str, product: ProductUpdate, db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.sku == sku).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = (
        db.query(Category)
        .filter(Category.name == product.category_name)
        .first()
    )
    if not category:
        category = Category(name=product.category_name)
        db.add(category)
        db.commit()
        db.refresh(category)

    db_product.name = product.name
    db_product.category_id = category.id
    db.commit()
    db.refresh(db_product)

    db_price = (
        db.query(Price).filter(Price.product_id == db_product.id).first()
    )
    db_price.amount = product.price
    db.commit()
    db.refresh(db_price)

    db_inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == db_product.id)
        .first()
    )
    db_inventory.quantity = product.quantity
    db.commit()
    db.refresh(db_inventory)

    return serialize_product(db_product)


@app.delete("/products/{sku}", response_model=ProductResponse)
def delete_product(sku: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.sku == sku).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_price = (
        db.query(Price).filter(Price.product_id == db_product.id).first()
    )
    db_inventory = (
        db.query(Inventory)
        .filter(Inventory.product_id == db_product.id)
        .first()
    )

    db.delete(db_inventory)
    db.delete(db_price)
    db.delete(db_product)
    db.commit()

    return serialize_product(db_product)
