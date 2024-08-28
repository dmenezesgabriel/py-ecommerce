from typing import List, Optional

from sqlalchemy.orm import Session
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.repositories.customer_repository import CustomerRepository
from src.infrastructure.persistence.models import CustomerModel


class SQLAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, customer: CustomerEntity):
        db_customer = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == customer.email)
            .first()
        )

        if not db_customer:
            db_customer = CustomerModel(
                name=customer.name,
                email=customer.email,
                phone_number=customer.phone_number,
            )
            self.db.add(db_customer)
        else:
            db_customer.name = customer.name
            db_customer.email = customer.email
            db_customer.phone_number = customer.phone_number

        self.db.commit()
        self.db.refresh(db_customer)
        customer.id = db_customer.id

    def find_by_email(self, email: str) -> Optional[CustomerEntity]:
        db_customer = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == email, CustomerModel.deleted == 0)
            .first()
        )
        if db_customer:
            return CustomerEntity(
                id=db_customer.id,
                name=db_customer.name,
                email=db_customer.email,
                phone_number=db_customer.phone_number,
            )
        return None

    def list_all(self) -> List[CustomerEntity]:
        db_customers = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.deleted == 0)
            .all()
        )
        return [
            CustomerEntity(
                id=db_customer.id,
                name=db_customer.name,
                email=db_customer.email,
                phone_number=db_customer.phone_number,
            )
            for db_customer in db_customers
        ]

    def delete(self, customer: CustomerEntity):
        db_customer = (
            self.db.query(CustomerModel)
            .filter(CustomerModel.id == customer.id)
            .first()
        )

        if db_customer:
            db_customer.name = f"deleted_user_{db_customer.id}"
            db_customer.email = f"deleted_email_{db_customer.id}@example.com"
            db_customer.phone_number = f"deleted_phone_number_{db_customer.id}"

            # Anonymize related addresses
            for delivery in db_customer.deliveries:
                if delivery.address:
                    delivery.delivery_address = (
                        f"deleted_address_{delivery.address.id}"
                    )
                    delivery.address.city = (
                        f"deleted_city_{delivery.address.id}"
                    )
                    delivery.address.state = (
                        f"deleted_state_{delivery.address.id}"
                    )
                    delivery.address.country = (
                        f"deleted_country_{delivery.address.id}"
                    )
                    delivery.address.zip_code = (
                        f"deleted_zip_{delivery.address.id}"
                    )
                    delivery.address.deleted = 1

            db_customer.deleted = 1
            self.db.commit()
