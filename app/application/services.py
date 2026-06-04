from __future__ import annotations

from datetime import datetime

from app.domain.exceptions import DuplicateSKUError, ProductNotFoundError
from app.domain.models import MovementType, Product, Sale, StockMovement
from app.domain.repositories import MovementRepository, ProductRepository, SaleRepository


class ProductService:
    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository

    def create_product(
        self,
        sku: str,
        name: str,
        description: str,
        price: float,
        stock: int = 0,
        is_active: bool = True,
    ) -> Product:
        normalized_sku = sku.strip().upper()
        if self.product_repository.get_by_sku(normalized_sku):
            raise DuplicateSKUError(f"Ya existe un producto con SKU {normalized_sku}.")

        product = Product(
            sku=normalized_sku,
            name=name,
            description=description,
            price=round(price, 2),
            stock=stock,
            is_active=is_active,
        )
        self.product_repository.add(product)
        return product

    def update_product(
        self,
        sku: str,
        name: str,
        description: str,
        price: float,
        is_active: bool,
    ) -> Product:
        product = self.get_product(sku)
        product.update_details(name, description, round(price, 2), is_active)
        self.product_repository.update(product)
        return product

    def get_product(self, sku: str) -> Product:
        product = self.product_repository.get_by_sku(sku.strip().upper())
        if not product:
            raise ProductNotFoundError("No se encontró el producto solicitado.")
        return product

    def list_products(self, active_only: bool = False) -> list[Product]:
        if active_only:
            return self.product_repository.list_active()
        return self.product_repository.list_all()


class InventoryService:
    def __init__(
        self,
        product_repository: ProductRepository,
        movement_repository: MovementRepository,
    ) -> None:
        self.product_repository = product_repository
        self.movement_repository = movement_repository

    def record_entry(self, sku: str, quantity: int, reason: str) -> StockMovement:
        product = self._get_product(sku)
        product.increase_stock(quantity)
        self.product_repository.update(product)

        movement = StockMovement(
            product_sku=product.sku,
            movement_type=MovementType.ENTRY,
            quantity=quantity,
            reason=reason,
        )
        self.movement_repository.add(movement)
        return movement

    def record_exit(self, sku: str, quantity: int, reason: str) -> StockMovement:
        product = self._get_product(sku)
        product.decrease_stock(quantity)
        self.product_repository.update(product)

        movement = StockMovement(
            product_sku=product.sku,
            movement_type=MovementType.EXIT,
            quantity=quantity,
            reason=reason,
        )
        self.movement_repository.add(movement)
        return movement

    def list_product_history(self, sku: str) -> list[StockMovement]:
        product = self._get_product(sku)
        return self.movement_repository.list_by_product(product.sku)

    def list_recent_movements(self, limit: int = 10) -> list[StockMovement]:
        return self.movement_repository.list_recent(limit)

    def _get_product(self, sku: str) -> Product:
        product = self.product_repository.get_by_sku(sku.strip().upper())
        if not product:
            raise ProductNotFoundError("No se encontró el producto solicitado.")
        return product


class SalesService:
    def __init__(
        self,
        product_repository: ProductRepository,
        movement_repository: MovementRepository,
        sale_repository: SaleRepository,
    ) -> None:
        self.product_repository = product_repository
        self.movement_repository = movement_repository
        self.sale_repository = sale_repository

    def register_sale(self, sku: str, quantity: int) -> Sale:
        product = self.product_repository.get_by_sku(sku.strip().upper())
        if not product:
            raise ProductNotFoundError("No se encontró el producto solicitado.")

        product.decrease_stock(quantity)
        self.product_repository.update(product)

        sale = Sale(
            product_sku=product.sku,
            product_name=product.name,
            unit_price=product.price,
            quantity=quantity,
            total=round(product.price * quantity, 2),
        )
        self.sale_repository.add(sale)

        movement = StockMovement(
            product_sku=product.sku,
            movement_type=MovementType.SALE,
            quantity=quantity,
            reason="Venta rápida",
        )
        self.movement_repository.add(movement)
        return sale

    def list_recent_sales(self, limit: int = 10) -> list[Sale]:
        return self.sale_repository.list_recent(limit)


class DashboardService:
    def __init__(
        self,
        product_repository: ProductRepository,
        movement_repository: MovementRepository,
        sale_repository: SaleRepository,
        low_stock_threshold: int,
    ) -> None:
        self.product_repository = product_repository
        self.movement_repository = movement_repository
        self.sale_repository = sale_repository
        self.low_stock_threshold = low_stock_threshold

    def get_summary(self) -> dict:
        products = self.product_repository.list_all()
        today = datetime.now().date()
        todays_sales = self.sale_repository.list_by_date(today)

        return {
            "total_products": len(products),
            "active_products": sum(1 for product in products if product.is_active),
            "low_stock_products": sum(
                1 for product in products if product.stock <= self.low_stock_threshold
            ),
            "sales_today_count": len(todays_sales),
            "sales_today_total": round(sum(sale.total for sale in todays_sales), 2),
            "recent_movements": self.movement_repository.list_recent(8),
            "recent_sales": self.sale_repository.list_recent(5),
        }
