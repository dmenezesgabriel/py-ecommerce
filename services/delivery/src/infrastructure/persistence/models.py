from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.domain.entities.delivery_entity import DeliveryStatus
from src.infrastructure.persistence.db_setup import Base


class DeliveryModel(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    delivery_address = Column(String)
    delivery_date = Column(String)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    customer = relationship("CustomerModel", back_populates="deliveries")
    address = relationship(
        "AddressModel", uselist=False, back_populates="delivery"
    )


class CustomerModel(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    deleted = Column(Integer, default=0)  # Logical delete column
    deliveries = relationship("DeliveryModel", back_populates="customer")


class AddressModel(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    deleted = Column(Integer, default=0)  # Logical delete column for address
    delivery = relationship(
        "DeliveryModel", uselist=False, back_populates="address"
    )
