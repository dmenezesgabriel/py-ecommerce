import unittest

from src.application.dto.health_dto import HealthResponse


class TestHealthResponseDTO(unittest.TestCase):

    def test_health_response_dto(self):
        # Arrange
        data = {
            "database": "healthy",
            "rabbitmq": "healthy",
        }

        # Act
        health_response = HealthResponse(**data)

        # Assert
        self.assertEqual(health_response.database, data["database"])
        self.assertEqual(health_response.rabbitmq, data["rabbitmq"])

    def test_health_response_examples(self):
        # Arrange
        examples = HealthResponse.model_config["json_schema_extra"]["examples"]

        # Act
        example_1 = HealthResponse(**examples[0])

        # Assert
        self.assertEqual(example_1.database, "healthy")
        self.assertEqual(example_1.rabbitmq, "healthy")


if __name__ == "__main__":
    unittest.main()
