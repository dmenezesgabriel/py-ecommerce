# payment_service.py

import os
from enum import Enum
from typing import List, Optional

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


# Custom Exceptions
class EntityNotFound(Exception):
    pass


class EntityAlreadyExists(Exception):
    pass


# Entities
class PaymentEntity:
    def __init__(
        self,
        order_id: int,
        amount: float,
        status: str,
        id: Optional[str] = None,
    ):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.status = status

    def update_status(self, new_status: str):
        self.status = new_status


# Services
class PaymentService:
    def __init__(self, payment_repository):
        self.payment_repository = payment_repository

    def create_payment(
        self, order_id: int, amount: float, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_order_id(order_id)
        if payment:
            raise EntityAlreadyExists(
                f"Payment with order_id '{order_id}' already exists"
            )

        payment_entity = PaymentEntity(
            order_id=order_id, amount=amount, status=status
        )
        self.payment_repository.save(payment_entity)
        return payment_entity

    def get_payment_by_id(self, payment_id: str) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")
        return payment

    def get_payment_by_order_id(self, order_id: int) -> PaymentEntity:
        payment = self.payment_repository.find_by_order_id(order_id)
        if not payment:
            raise EntityNotFound(
                f"Payment with order_id '{order_id}' not found"
            )
        return payment

    def update_payment(
        self, payment_id: str, order_id: int, amount: float, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        payment.order_id = order_id
        payment.amount = amount
        payment.status = status
        self.payment_repository.save(payment)
        return payment

    def update_payment_status(
        self, payment_id: str, status: str
    ) -> PaymentEntity:
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        payment.update_status(status)
        self.payment_repository.save(payment)
        return payment

    def delete_payment(self, payment_id: str):
        payment = self.payment_repository.find_by_id(payment_id)
        if not payment:
            raise EntityNotFound(f"Payment with ID '{payment_id}' not found")

        self.payment_repository.delete(payment)
        return payment


# Ports (Interfaces)
class PaymentRepository:
    def save(self, payment: PaymentEntity):
        raise NotImplementedError

    def find_by_id(self, payment_id: str) -> Optional[PaymentEntity]:
        raise NotImplementedError

    def find_by_order_id(self, order_id: int) -> Optional[PaymentEntity]:
        raise NotImplementedError

    def delete(self, payment: PaymentEntity):
        raise NotImplementedError


# Adapters (Repository Implementation)
class MongoDBPaymentRepository(PaymentRepository):
    def __init__(self, db):
        self.db = db

    def save(self, payment: PaymentEntity):
        if payment.id:
            self.db.replace_one(
                {"_id": ObjectId(payment.id)}, payment.__dict__
            )
        else:
            result = self.db.insert_one(payment.__dict__)
            payment.id = str(result.inserted_id)

    def find_by_id(self, payment_id: str) -> Optional[PaymentEntity]:
        payment_data = self.db.find_one({"_id": ObjectId(payment_id)})
        if payment_data:
            return PaymentEntity(
                id=str(payment_data["_id"]),
                order_id=payment_data["order_id"],
                amount=payment_data["amount"],
                status=payment_data["status"],
            )
        return None

    def find_by_order_id(self, order_id: int) -> Optional[PaymentEntity]:
        payment_data = self.db.find_one({"order_id": order_id})
        if payment_data:
            return PaymentEntity(
                id=str(payment_data["_id"]),
                order_id=payment_data["order_id"],
                amount=payment_data["amount"],
                status=payment_data["status"],
            )
        return None

    def delete(self, payment: PaymentEntity):
        self.db.delete_one({"_id": ObjectId(payment.id)})


# FastAPI Routes (Adapter)
@app.on_event("startup")
def on_startup():
    # Clear all existing data
    payments_collection.delete_many(
        {}
    )  # Clear all documents from the collection


def get_payment_service() -> PaymentService:
    payment_repository = MongoDBPaymentRepository(payments_collection)
    return PaymentService(payment_repository)


# Pydantic Models for API
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    status: PaymentStatus


class PaymentUpdate(BaseModel):
    order_id: int
    amount: float
    status: PaymentStatus


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: str
    order_id: int
    amount: float
    status: PaymentStatus

    class Config:
        orm_mode = True
        json_encoders = {
            ObjectId: str,
        }


@app.post("/payments/", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        created_payment = service.create_payment(
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        return serialize_payment(created_payment)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/payments/", response_model=List[PaymentResponse])
def read_payments(service: PaymentService = Depends(get_payment_service)):
    payments = service.payment_repository.db.find()
    return [
        serialize_payment(
            PaymentEntity(
                id=str(payment["_id"]),
                order_id=payment["order_id"],
                amount=payment["amount"],
                status=payment["status"],
            )
        )
        for payment in payments
    ]


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def read_payment(
    payment_id: str, service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = service.get_payment_by_id(payment_id)
        return serialize_payment(payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/payments/by-order-id/{order_id}", response_model=PaymentResponse)
def read_payment_by_order_id(
    order_id: int, service: PaymentService = Depends(get_payment_service)
):
    try:
        payment = service.get_payment_by_order_id(order_id)
        return serialize_payment(payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: str,
    payment: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment(
            payment_id=payment_id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/payments/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: str,
    status_update: PaymentStatusUpdate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        updated_payment = service.update_payment_status(
            payment_id, status_update.status
        )
        return serialize_payment(updated_payment)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: str, service: PaymentService = Depends(get_payment_service)
):
    try:
        service.delete_payment(payment_id)
        return {"detail": "Payment deleted"}
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


# Serialization Function
def serialize_payment(payment: PaymentEntity) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        amount=payment.amount,
        status=payment.status,
    )
