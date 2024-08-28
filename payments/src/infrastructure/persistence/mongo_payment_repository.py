from typing import Optional

from bson.objectid import ObjectId
from src.domain.entities.payment_entity import PaymentEntity
from src.domain.repositories.payment_repository import PaymentRepository


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
                qr_code=payment_data.get("qr_code"),
                qr_code_expiration=payment_data.get("qr_code_expiration"),
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
                qr_code=payment_data.get("qr_code"),
                qr_code_expiration=payment_data.get("qr_code_expiration"),
            )
        return None

    def delete(self, payment: PaymentEntity):
        self.db.delete_one({"_id": ObjectId(payment.id)})
