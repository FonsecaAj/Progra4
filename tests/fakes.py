from __future__ import annotations

from datetime import date

from app.domain.models import Product, Sale, StockMovement
from app.domain.repositories import MovementRepository, ProductRepository, SaleRepository


class FakeProductRepository(ProductRepository):
    def __init__(self) -> None:
        self.products: dict[str, Product] = {}

    def add(self, product: Product) -> None:
        self.products[product.sku] = product

    def get_by_sku(self, sku: str) -> Product | None:
        return self.products.get(sku.strip().upper())

    def list_all(self) -> list[Product]:
        return sorted(self.products.values(), key=lambda product: product.created_at, reverse=True)

    def list_active(self) -> list[Product]:
        return [product for product in self.list_all() if product.is_active]

    def update(self, product: Product) -> None:
        self.products[product.sku] = product


class FakeMovementRepository(MovementRepository):
    def __init__(self) -> None:
        self.movements: list[StockMovement] = []

    def add(self, movement: StockMovement) -> None:
        self.movements.append(movement)

    def list_by_product(self, sku: str) -> list[StockMovement]:
        normalized = sku.strip().upper()
        return [movement for movement in reversed(self.movements) if movement.product_sku == normalized]

    def list_recent(self, limit: int = 10) -> list[StockMovement]:
        return list(reversed(self.movements))[:limit]


class FakeSaleRepository(SaleRepository):
    def __init__(self) -> None:
        self.sales: list[Sale] = []

    def add(self, sale: Sale) -> None:
        self.sales.append(sale)

    def list_recent(self, limit: int = 10) -> list[Sale]:
        return list(reversed(self.sales))[:limit]

    def list_by_date(self, day: date) -> list[Sale]:
        return [sale for sale in reversed(self.sales) if sale.created_at.date() == day]
