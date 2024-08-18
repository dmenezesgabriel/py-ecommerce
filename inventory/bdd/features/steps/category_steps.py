import logging
import os
import random
import string

import requests
from behave import given, then, when

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

BASE_URL = os.getenv("BASE_URL")


def generate_random_category_name():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


@given("the inventory service is running")
def step_given_inventory_service_is_running(context):
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200


@when("I create a random category")
def step_when_create_random_category(context):
    context.category_name = generate_random_category_name()
    payload = {"name": context.category_name}
    response = requests.post(f"{BASE_URL}/categories/", json=payload)

    assert response.status_code == 200
    context.category_id = response.json()["id"]


@then("the category should be listed in the categories")
def step_then_category_should_be_listed(context):
    response = requests.get(f"{BASE_URL}/categories/")
    assert response.status_code == 200
    categories = response.json()
    category_names = [category["name"] for category in categories]
    assert context.category_name in category_names
