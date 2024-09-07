Feature: Category management
  As a user
  I want to manage categories
  So that I can organize my products

  Scenario: Create and list a random category
    Given the inventory service is running
    When I create a random category
    Then the category should be listed in the categories
