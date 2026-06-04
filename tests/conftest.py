from __future__ import annotations

import pytest

from app import create_app
from app.application.services import DashboardService, InventoryService, ProductService, SalesService
from app.config import AppConfig
from app.container import ServiceContainer
from tests.fakes import FakeMovementRepository, FakeProductRepository, FakeSaleRepository


@pytest.fixture
def fake_repositories():
    products = FakeProductRepository()
    movements = FakeMovementRepository()
    sales = FakeSaleRepository()
    return products, movements, sales


@pytest.fixture
def service_container(fake_repositories):
    products, movements, sales = fake_repositories
    config = AppConfig(
        SECRET_KEY="test-secret",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DATABASE="inventory_web_demo_test",
        LOW_STOCK_THRESHOLD=5,
        TESTING=True,
    )
    return ServiceContainer(
        config=config,
        product_service=ProductService(products),
        inventory_service=InventoryService(products, movements),
        sales_service=SalesService(products, movements, sales),
        dashboard_service=DashboardService(products, movements, sales, config.LOW_STOCK_THRESHOLD),
    )


@pytest.fixture
def app(service_container):
    return create_app(
        config_override={"TESTING": True, "SECRET_KEY": "test-secret"},
        services=service_container,
    )


@pytest.fixture
def client(app):
    return app.test_client()
