import pytest
from main import app


class TestApp:

    def test_include_routers(self):
        # Act
        router_paths = [route.path for route in app.routes]

        # Assert
        assert "/categories/" in router_paths
        assert "/products/" in router_paths
        assert "/inventory/{sku}/add" in router_paths
        assert "/health" in router_paths


if __name__ == "__main__":
    pytest.main()
