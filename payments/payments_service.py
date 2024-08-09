import os
from enum import Enum
from typing import List

import pymongo
from bson.objectid import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient

app = FastAPI()

# MongoDB setup
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "payments")
MONGO_USER = os.getenv("MONGO_USER", "mongo")
MONGO_PASS = os.getenv("MONGO_PASS", "mongo")

client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER,
    password=MONGO_PASS,
)
db = client[MONGO_DB]
payments_collection = db["payments"]


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(BaseModel):
    id: str = Field(default=None)
    order_id: int
    amount: float
    status: PaymentStatus

    class Config:
        orm_mode = True
        json_encoders = {
            ObjectId: str,
        }


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


@app.on_event("startup")
def on_startup():
    # Clear all existing data
    payments_collection.delete_many(
        {}
    )  # Clear all documents from the collection


@app.post("/payments/", response_model=Payment)
def create_payment(payment: Payment):
    # Check if order_id already exists
    if payments_collection.find_one({"order_id": payment.order_id}):
        raise HTTPException(
            status_code=400, detail="Payment with this order_id already exists"
        )

    payment_dict = payment.dict(exclude_unset=True)
    result = payments_collection.insert_one(payment_dict)
    payment_dict["id"] = str(result.inserted_id)
    return Payment(**payment_dict)


@app.get("/payments/", response_model=List[Payment])
def read_payments():
    payments = payments_collection.find()
    return [Payment(**payment, id=str(payment["_id"])) for payment in payments]


@app.get("/payments/{payment_id}", response_model=Payment)
def read_payment(payment_id: str):
    payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment["id"] = str(payment["_id"])
    return Payment(**payment)


@app.get("/payments/by-order-id/{order_id}", response_model=Payment)
def read_payment_by_order_id(order_id: int):
    payment = payments_collection.find_one({"order_id": order_id})
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment["id"] = str(payment["_id"])
    return Payment(**payment)


@app.put("/payments/{payment_id}", response_model=Payment)
def update_payment(payment_id: str, payment: Payment):
    existing_payment = payments_collection.find_one(
        {"_id": ObjectId(payment_id)}
    )
    if existing_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment_dict = payment.dict(exclude_unset=True)
    payments_collection.replace_one(
        {"_id": ObjectId(payment_id)}, payment_dict
    )
    payment_dict["id"] = payment_id
    return Payment(**payment_dict)


@app.put("/payments/{payment_id}/status", response_model=Payment)
def update_payment_status(payment_id: str, status_update: PaymentStatusUpdate):
    existing_payment = payments_collection.find_one(
        {"_id": ObjectId(payment_id)}
    )
    if existing_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payments_collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"status": status_update.status}},
    )
    updated_payment = payments_collection.find_one(
        {"_id": ObjectId(payment_id)}
    )
    updated_payment["id"] = payment_id
    return Payment(**updated_payment)


@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: str):
    result = payments_collection.delete_one({"_id": ObjectId(payment_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"detail": "Payment deleted"}
