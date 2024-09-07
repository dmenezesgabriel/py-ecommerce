from typing import List, Optional

from sqlalchemy.orm import Session
from src.domain.entities.address_entity import AddressEntity
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.entities.delivery_entity import DeliveryEntity
from src.domain.repositories.delivery_repository import DeliveryRepository
from src.infrastructure.persistence.models import (
    AddressModel,
    CustomerModel,
    DeliveryModel,
)


class SQLAlchemyDeliveryRepository(DeliveryRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, delivery: DeliveryEntity):
        customer_model = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == delivery.customer.email)
            .first()
        )
        if not customer_model:
            customer_model = CustomerModel(
                name=delivery.customer.name,
                email=delivery.customer.email,
                phone_number=delivery.customer.phone_number,
            )
            self.db.add(customer_model)
            self.db.commit()
            self.db.refresh(customer_model)

        if delivery.id:
            db_delivery = (
                self.db.query(DeliveryModel)
                .filter(DeliveryModel.id == delivery.id)
                .first()
            )
        else:
            db_delivery = DeliveryModel(
                order_id=delivery.order_id,
                delivery_address=delivery.delivery_address,
                delivery_date=delivery.delivery_date,
                status=delivery.status,
                customer_id=customer_model.id,
            )
            self.db.add(db_delivery)
            self.db.commit()
            self.db.refresh(db_delivery)

        address_model = AddressModel(
            city=delivery.address.city,
            state=delivery.address.state,
            country=delivery.address.country,
            zip_code=delivery.address.zip_code,
            delivery=db_delivery,
        )
        self.db.add(address_model)
        self.db.commit()
        self.db.refresh(address_model)

        db_delivery.address = address_model
        self.db.commit()
        self.db.refresh(db_delivery)
        delivery.id = db_delivery.id
        delivery.customer.id = customer_model.id
        delivery.address.id = address_model.id

    def find_by_id(self, delivery_id: int) -> Optional[DeliveryEntity]:
        db_delivery = (
            self.db.query(DeliveryModel)
            .filter(DeliveryModel.id == delivery_id)
            .first()
        )
        if db_delivery:
            return DeliveryEntity(
                id=db_delivery.id,
                order_id=db_delivery.order_id,
                delivery_address=db_delivery.delivery_address,
                delivery_date=db_delivery.delivery_date,
                status=db_delivery.status,
                customer=CustomerEntity(
                    id=db_delivery.customer.id,
                    name=db_delivery.customer.name,
                    email=db_delivery.customer.email,
                    phone_number=db_delivery.customer.phone_number,
                ),
                address=AddressEntity(
                    id=db_delivery.address.id,
                    city=db_delivery.address.city,
                    state=db_delivery.address.state,
                    country=db_delivery.address.country,
                    zip_code=db_delivery.address.zip_code,
                ),
            )
        return None

    def find_by_order_id(self, order_id: int) -> Optional[DeliveryEntity]:
        db_delivery = (
            self.db.query(DeliveryModel)
            .filter(DeliveryModel.order_id == order_id)
            .first()
        )
        if db_delivery:
            return DeliveryEntity(
                id=db_delivery.id,
                order_id=db_delivery.order_id,
                delivery_address=db_delivery.delivery_address,
                delivery_date=db_delivery.delivery_date,
                status=db_delivery.status,
                customer=CustomerEntity(
                    id=db_delivery.customer.id,
                    name=db_delivery.customer.name,
                    email=db_delivery.customer.email,
                    phone_number=db_delivery.customer.phone_number,
                ),
                address=AddressEntity(
                    id=db_delivery.address.id,
                    city=db_delivery.address.city,
                    state=db_delivery.address.state,
                    country=db_delivery.address.country,
                    zip_code=db_delivery.address.zip_code,
                ),
            )
        return None

    def delete(self, delivery: DeliveryEntity):
        db_delivery = (
            self.db.query(DeliveryModel)
            .filter(DeliveryModel.id == delivery.id)
            .first()
        )
        if db_delivery:
            self.db.delete(db_delivery.address)
            self.db.delete(db_delivery)
            self.db.commit()

    def list_all(self) -> List[DeliveryEntity]:
        db_deliveries = self.db.query(DeliveryModel).all()
        return [
            DeliveryEntity(
                id=db_delivery.id,
                order_id=db_delivery.order_id,
                delivery_address=db_delivery.delivery_address,
                delivery_date=db_delivery.delivery_date,
                status=db_delivery.status,
                customer=CustomerEntity(
                    id=db_delivery.customer.id,
                    name=db_delivery.customer.name,
                    email=db_delivery.customer.email,
                    phone_number=db_delivery.customer.phone_number,
                ),
                address=AddressEntity(
                    id=db_delivery.address.id,
                    city=db_delivery.address.city,
                    state=db_delivery.address.state,
                    country=db_delivery.address.country,
                    zip_code=db_delivery.address.zip_code,
                ),
            )
            for db_delivery in db_deliveries
        ]
