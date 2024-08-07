from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

app = FastAPI()

DATABASE_URL = "sqlite:///./data/orders.db"

# Ensure the data directory exists
if not os.path.exists('/app/data'):
    os.makedirs('/app/data')

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer)
    total_price = Column(Float)
    customer_name = Column(String)
    customer_address = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic model for Order
class OrderCreate(BaseModel):
    product_id: int
    quantity: int
    total_price: float
    customer_name: str
    customer_address: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/orders/")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=order.total_price,
        customer_name=order.customer_name,
        customer_address=order.customer_address
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return {"message": "Order created successfully", "order": db_order}

@app.get("/orders/")
def read_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return {"orders": orders}

@app.get("/orders/{order_id}")
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": order}

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.product_id = order.product_id
    db_order.quantity = order.quantity
    db_order.total_price = order.total_price
    db_order.customer_name = order.customer_name
    db_order.customer_address = order.customer_address
    db.commit()
    db.refresh(db_order)
    return {"message": "Order updated successfully"}

@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted successfully"}
