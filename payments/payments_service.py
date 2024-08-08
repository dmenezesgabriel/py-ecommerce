import os
from enum import Enum
from typing import List

import tinydb
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from tinydb import Query

app = FastAPI()

# Database setup
db_file = "payments.json"

# Ensure the data file exists
if not os.path.exists(db_file):
    open(db_file, "w").close()  # Create an empty file if it doesn't exist

db = tinydb.TinyDB(db_file)
payments_table = db.table("payments")


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(BaseModel):
    id: int
    order_id: int
    amount: float
    status: PaymentStatus


class PaymentStatusUpdate(BaseModel):
    status: PaymentStatus


@app.on_event("startup")
def on_startup():
    # Clear all existing data
    db.truncate()  # Clear all data from all tables/collections

    # Optionally, you can prepopulate with default data here
    # Example: payments_table.insert({"id": 1, "order_id": 1, "amount": 100.0, "status": "pending"})


@app.post("/payments/", response_model=Payment)
def create_payment(payment: Payment):
    # Check if ID already exists
    if payments_table.get(Query().id == payment.id):
        raise HTTPException(
            status_code=400, detail="Payment with this ID already exists"
        )

    payments_table.insert(payment.dict())
    return payment


@app.get("/payments/", response_model=List[Payment])
def read_payments():
    payments = payments_table.all()
    # Adjust data to match Pydantic model
    return [
        Payment(
            id=payment.get("id"),
            order_id=payment.get("order_id"),
            amount=payment.get("amount"),
            status=PaymentStatus(payment.get("status")),
        )
        for payment in payments
    ]


@app.get("/payments/{payment_id}", response_model=Payment)
def read_payment(payment_id: int):
    payment = payments_table.get(Query().id == payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Payment(
        id=payment.get("id"),
        order_id=payment.get("order_id"),
        amount=payment.get("amount"),
        status=PaymentStatus(payment.get("status")),
    )


@app.get("/payments/by-order-id/{order_id}", response_model=Payment)
def read_payment_by_order_id(order_id: int):
    payment = payments_table.get(Query().order_id == order_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Payment(
        id=payment.get("id"),
        order_id=payment.get("order_id"),
        amount=payment.get("amount"),
        status=PaymentStatus(payment.get("status")),
    )


@app.put("/payments/{payment_id}", response_model=Payment)
def update_payment(payment_id: int, payment: Payment):
    existing_payment = payments_table.get(Query().id == payment_id)
    if existing_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payments_table.update(payment.dict(), Query().id == payment_id)
    return payment


@app.put("/payments/{payment_id}/status", response_model=Payment)
def update_payment_status(payment_id: int, status_update: PaymentStatusUpdate):
    existing_payment = payments_table.get(Query().id == payment_id)
    if existing_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payments_table.update(
        {"status": status_update.status.value}, Query().id == payment_id
    )
    updated_payment = payments_table.get(Query().id == payment_id)
    return Payment(
        id=updated_payment.get("id"),
        order_id=updated_payment.get("order_id"),
        amount=updated_payment.get("amount"),
        status=PaymentStatus(updated_payment.get("status")),
    )


@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    if not payments_table.remove(Query().id == payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"detail": "Payment deleted"}
