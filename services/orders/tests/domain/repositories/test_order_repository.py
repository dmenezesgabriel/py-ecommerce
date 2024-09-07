from unittest.mock import MagicMock

import pytest
from src.domain.entities.order_entity import OrderEntity
from src.domain.repositories.order_repository import OrderRepository


def test_order_repository_has_save_method():
    assert hasattr(OrderRepository, "save")
    assert callable(getattr(OrderRepository, "save"))


def test_order_repository_has_find_by_id_method():
    assert hasattr(OrderRepository, "find_by_id")
    assert callable(getattr(OrderRepository, "find_by_id"))


def test_order_repository_has_find_by_order_number_method():
    assert hasattr(OrderRepository, "find_by_order_number")
    assert callable(getattr(OrderRepository, "find_by_order_number"))


def test_order_repository_has_delete_method():
    assert hasattr(OrderRepository, "delete")
    assert callable(getattr(OrderRepository, "delete"))


def test_order_repository_has_list_all_method():
    assert hasattr(OrderRepository, "list_all")
    assert callable(getattr(OrderRepository, "list_all"))
