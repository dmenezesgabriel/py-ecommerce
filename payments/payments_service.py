from typing import List

import tinydb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Database setup
db = tinydb.TinyDB("payments.json")
payments_table = db.table("payments")


class Payment(BaseModel):
    id: int
    order_id: int
    amount: float
    status: str


@app.post("/payments/", response_model=Payment)
def create_payment(payment: Payment):
    payments_table.insert(payment.dict())
    return payment


@app.get("/payments/", response_model=List[Payment])
def read_payments():
    payments = payments_table.all()
    return [Payment(**payment) for payment in payments]


@app.get("/payments/{payment_id}", response_model=Payment)
def read_payment(payment_id: int):
    payment = payments_table.get(tinydb.Query().id == payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return Payment(**payment)


@app.put("/payments/{payment_id}", response_model=Payment)
def update_payment(payment_id: int, payment: Payment):
    payments_table.update(payment.dict(), tinydb.Query().id == payment_id)
    return payment


@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    payments_table.remove(tinydb.Query().id == payment_id)
    return {"detail": "Payment deleted"}
