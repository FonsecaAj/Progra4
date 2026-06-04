from __future__ import annotations

from dataclasses import dataclass

from app.application.services import (
    DashboardService,
    InventoryService,
    ProductService,
    SalesService,
)
from app.config import AppConfig
from app.infrastructure.db import MongoSession
from app.infrastructure.repositories import (
    MongoMovementRepository,
    MongoProductRepository,
    MongoSaleRepository,
)


@dataclass
class ServiceContainer:
    config: AppConfig
    product_service: ProductService
    inventory_service: InventoryService
    sales_service: SalesService
    dashboard_service: DashboardService


def build_mongo_container(config: AppConfig) -> ServiceContainer:
    session = MongoSession(config.MONGODB_URI, config.MONGODB_DATABASE)
    session.ensure_indexes()

    product_repository = MongoProductRepository(session.database)
    movement_repository = MongoMovementRepository(session.database)
    sale_repository = MongoSaleRepository(session.database)

    product_service = ProductService(product_repository)
    inventory_service = InventoryService(product_repository, movement_repository)
    sales_service = SalesService(product_repository, movement_repository, sale_repository)
    dashboard_service = DashboardService(
        product_repository,
        movement_repository,
        sale_repository,
        config.LOW_STOCK_THRESHOLD,
    )

    return ServiceContainer(
        config=config,
        product_service=product_service,
        inventory_service=inventory_service,
        sales_service=sales_service,
        dashboard_service=dashboard_service,
    )
