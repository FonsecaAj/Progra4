from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.domain.models import Product, Sale, StockMovement


class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_sku(self, sku: str) -> Product | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    def list_active(self) -> list[Product]:
        raise NotImplementedError

    @abstractmethod
    def update(self, product: Product) -> None:
        raise NotImplementedError


class MovementRepository(ABC):
    @abstractmethod
    def add(self, movement: StockMovement) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_product(self, sku: str) -> list[StockMovement]:
        raise NotImplementedError

    @abstractmethod
    def list_recent(self, limit: int = 10) -> list[StockMovement]:
        raise NotImplementedError


class SaleRepository(ABC):
    @abstractmethod
    def add(self, sale: Sale) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_recent(self, limit: int = 10) -> list[Sale]:
        raise NotImplementedError

    @abstractmethod
    def list_by_date(self, day: date) -> list[Sale]:
        raise NotImplementedError
