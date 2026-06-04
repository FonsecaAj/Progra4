from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from app.domain.exceptions import (
    InactiveProductError,
    InsufficientStockError,
    InvalidPriceError,
    InvalidQuantityError,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MovementType(StrEnum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    SALE = "SALE"


@dataclass
class Product:
    sku: str
    name: str
    description: str
    price: float
    stock: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.sku = self.sku.strip().upper()
        self.name = self.name.strip()
        self.description = self.description.strip()
        self.validate_price(self.price)
        self.validate_quantity(self.stock, allow_zero=True)

    @staticmethod
    def validate_quantity(quantity: int, allow_zero: bool = False) -> None:
        minimum = 0 if allow_zero else 1
        if quantity < minimum:
            raise InvalidQuantityError("La cantidad debe ser mayor a cero.")

    @staticmethod
    def validate_price(price: float) -> None:
        if price <= 0:
            raise InvalidPriceError("El precio debe ser mayor a cero.")

    def update_details(
        self,
        name: str,
        description: str,
        price: float,
        is_active: bool,
    ) -> None:
        self.name = name.strip()
        self.description = description.strip()
        self.validate_price(price)
        self.price = round(price, 2)
        self.is_active = is_active

    def increase_stock(self, quantity: int) -> None:
        self.ensure_active()
        self.validate_quantity(quantity)
        self.stock += quantity

    def decrease_stock(self, quantity: int) -> None:
        self.ensure_active()
        self.validate_quantity(quantity)
        if self.stock - quantity < 0:
            raise InsufficientStockError("No hay stock suficiente para completar la operación.")
        self.stock -= quantity

    def ensure_active(self) -> None:
        if not self.is_active:
            raise InactiveProductError("El producto está inactivo.")


@dataclass
class StockMovement:
    product_sku: str
    movement_type: MovementType
    quantity: int
    reason: str
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.product_sku = self.product_sku.strip().upper()
        self.reason = self.reason.strip()
        Product.validate_quantity(self.quantity)


@dataclass
class Sale:
    product_sku: str
    product_name: str
    unit_price: float
    quantity: int
    total: float
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.product_sku = self.product_sku.strip().upper()
        self.product_name = self.product_name.strip()
        Product.validate_price(self.unit_price)
        Product.validate_quantity(self.quantity)
        if self.total <= 0:
            raise InvalidPriceError("El total de la venta debe ser mayor a cero.")
