from unittest.mock import patch

import pytest
from src.domain.entities.customer_entity import CustomerEntity
from src.domain.exceptions import InvalidEntity


def test_customer_entity_initialization():
    customer = CustomerEntity(
        name="John Doe",
        email="john@example.com",
        phone_number="+1234567890",
        id=1,
    )
    assert customer.id == 1
    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
    assert customer.phone_number == "+1234567890"


def test_customer_entity_initialization_with_defaults():
    customer = CustomerEntity(name="Jane Doe", email="jane@example.com")
    assert customer.id is None
    assert customer.name == "Jane Doe"
    assert customer.email == "jane@example.com"
    assert customer.phone_number is None


def test_customer_entity_invalid_id():
    with pytest.raises(InvalidEntity) as exc_info:
        CustomerEntity(name="John Doe", email="john@example.com", id=-1)
    assert str(exc_info.value) == "ID must be a positive integer."


def test_customer_entity_invalid_name():
    with pytest.raises(InvalidEntity) as exc_info:
        CustomerEntity(name="J", email="john@example.com")
    assert str(exc_info.value) == "Name must be at least 2 characters long."


def test_customer_entity_invalid_email():
    with pytest.raises(InvalidEntity) as exc_info:
        CustomerEntity(name="John Doe", email="invalid-email")
    assert str(exc_info.value) == "Invalid email format."


def test_customer_entity_invalid_phone_number():
    with pytest.raises(InvalidEntity) as exc_info:
        CustomerEntity(
            name="John Doe", email="john@example.com", phone_number="12345"
        )
    assert str(exc_info.value) == "Invalid phone number format."


def test_update_customer_name():
    customer = CustomerEntity(name="John Doe", email="john@example.com")
    customer.update_customer(name="Jane Doe")
    assert customer.name == "Jane Doe"


def test_update_customer_email():
    customer = CustomerEntity(name="John Doe", email="john@example.com")
    customer.update_customer(email="jane@example.com")
    assert customer.email == "jane@example.com"


def test_update_customer_phone_number():
    customer = CustomerEntity(
        name="John Doe", email="john@example.com", phone_number="+1234567890"
    )
    customer.update_customer(phone_number="+0987654321")
    assert customer.phone_number == "+0987654321"


def test_to_dict():
    customer = CustomerEntity(
        name="John Doe",
        email="john@example.com",
        phone_number="+1234567890",
        id=1,
    )
    expected_dict = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+1234567890",
    }
    assert customer.to_dict() == expected_dict


@patch("src.domain.entities.customer_entity.re.match")
def test_phone_number_validation_regex_match(mock_match):
    mock_match.side_effect = [
        True,
        True,
    ]  # First call for email, second for phone number
    customer = CustomerEntity(
        name="John Doe", email="john@example.com", phone_number="+1234567890"
    )

    # Verify the second call (phone number validation)
    mock_match.assert_any_call(r"^\+\d{1,3}\d{1,14}$", "+1234567890")
    assert customer.phone_number == "+1234567890"
