import logging
import os
import random
import string

import requests
from behave import given, then, when

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

BASE_URL = os.getenv("BASE_URL")

# Fixed product details
PRODUCT_NAME = "Test Product"
UPDATED_PRODUCT_NAME = "Updated Test Product"


def generate_random_sku():
    """Generates a random SKU to avoid conflicts during testing."""
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=10)
    )


@given("a random category exists")
def step_given_a_random_category_exists(context):
    context.category_name = "".join(
        random.choices(string.ascii_letters + string.digits, k=10)
    )
    payload = {"name": context.category_name}
    response = requests.post(f"{BASE_URL}/categories/", json=payload)
    assert response.status_code == 200
    context.category_id = response.json()["id"]


@when("I create a product")
def step_when_create_product(context):
    context.product_sku = generate_random_sku()
    payload = {
        "sku": context.product_sku,
        "name": PRODUCT_NAME,
        "category_name": context.category_name,
        "price": 99.99,
        "quantity": 10,
    }
    response = requests.post(f"{BASE_URL}/products/", json=payload)
    logger.info(response.json())
    assert response.status_code == 200


@then("I should be able to retrieve the product by SKU")
def step_then_retrieve_product_by_sku(context):
    response = requests.get(f"{BASE_URL}/products/{context.product_sku}")
    assert response.status_code == 200
    product = response.json()
    logger.info(f"Retrieved Product: {product}")
    assert product["sku"] == context.product_sku
    assert product["name"] == PRODUCT_NAME


@when("I update the product")
def step_when_update_product(context):
    payload = {
        "name": UPDATED_PRODUCT_NAME,
        "category_name": context.category_name,
        "price": 109.99,
        "quantity": 20,
    }
    response = requests.put(
        f"{BASE_URL}/products/{context.product_sku}", json=payload
    )
    logger.info(f"Update response: {response.json()}")
    assert response.status_code == 200


@then("the product should be updated with new details")
def step_then_product_should_be_updated(context):
    response = requests.get(f"{BASE_URL}/products/{context.product_sku}")
    assert response.status_code == 200
    product = response.json()
    logger.info(f"Updated Product: {product}")
    assert product["name"] == UPDATED_PRODUCT_NAME
    assert product["price"] == 109.99
    assert product["quantity"] == 20


@then("the product should be listed in all products")
def step_then_product_should_be_listed_in_all(context):
    response = requests.get(f"{BASE_URL}/products/")
    assert response.status_code == 200
    products = response.json()
    product_skus = [product["sku"] for product in products]
    logger.info(f"All Products: {products}")
    assert context.product_sku in product_skus


@then("the product should be listed under its category")
def step_then_product_should_be_listed_by_category(context):
    response = requests.get(
        f"{BASE_URL}/products/by-category/{context.category_name}"
    )
    assert response.status_code == 200
    products = response.json()
    product_skus = [product["sku"] for product in products]
    logger.info(f"Products by Category: {products}")
    assert context.product_sku in product_skus


@when("I delete the product by SKU")
def step_when_delete_product_by_sku(context):
    response = requests.delete(f"{BASE_URL}/products/{context.product_sku}")
    if response.status_code != 200:
        logger.error(
            f"Failed to delete product with SKU {context.product_sku}. Status code: {response.status_code}"
        )
    assert response.status_code == 200


@then("the product should not be found by SKU")
def step_then_product_should_not_be_found_by_sku(context):
    response = requests.get(f"{BASE_URL}/products/{context.product_sku}")
    assert response.status_code == 404
