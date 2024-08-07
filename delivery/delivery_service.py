from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

app = FastAPI()

DATABASE_URL = "sqlite:///./data/deliveries.db"

# Ensure the data directory exists
if not os.path.exists('/app/data'):
    os.makedirs('/app/data')

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    delivery_address = Column(String)
    delivery_date = Column(String)
    status = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic model for Delivery
class DeliveryCreate(BaseModel):
    order_id: int
    delivery_address: str
    delivery_date: str
    status: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/deliveries/")
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    db_delivery = Delivery(
        order_id=delivery.order_id,
        delivery_address=delivery.delivery_address,
        delivery_date=delivery.delivery_date,
        status=delivery.status
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return {"message": "Delivery created successfully", "delivery": db_delivery}

@app.get("/deliveries/")
def read_deliveries(db: Session = Depends(get_db)):
    deliveries = db.query(Delivery).all()
    return {"deliveries": deliveries}

@app.get("/deliveries/{delivery_id}")
def read_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return {"delivery": delivery}

@app.put("/deliveries/{delivery_id}")
def update_delivery(delivery_id: int, delivery: DeliveryCreate, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db_delivery.order_id = delivery.order_id
    db_delivery.delivery_address = delivery.delivery_address
    db_delivery.delivery_date = delivery.delivery_date
    db_delivery.status = delivery.status
    db.commit()
    db.refresh(db_delivery)
    return {"message": "Delivery updated successfully"}

@app.delete("/deliveries/{delivery_id}")
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(db_delivery)
    db.commit()
    return {"message": "Delivery deleted successfully"}
