Feature: Product management
  As a user
  I want to manage products
  So that I can organize my inventory

  Scenario: Create a product
    Given the inventory service is running
    And a random category exists
    When I create a product
    Then I should be able to retrieve the product by SKU

  Scenario: Update a product
    Given the inventory service is running
    And a random category exists
    When I create a product
    And I update the product
    Then the product should be updated with new details

  Scenario: List all products
    Given the inventory service is running
    And a random category exists
    When I create a product
    Then the product should be listed in all products

  Scenario: Filter products by category
    Given the inventory service is running
    And a random category exists
    When I create a product
    Then the product should be listed under its category

  Scenario: Delete a product
    Given the inventory service is running
    And a random category exists
    When I create a product
    And I delete the product by SKU
    Then the product should not be found by SKU
