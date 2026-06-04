from __future__ import annotations

from datetime import date, datetime, time, timezone

from pymongo import DESCENDING
from pymongo.database import Database

from app.domain.models import MovementType, Product, Sale, StockMovement
from app.domain.repositories import MovementRepository, ProductRepository, SaleRepository


def _serialize_product(product: Product) -> dict:
    return {
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "is_active": product.is_active,
        "created_at": product.created_at,
    }


def _deserialize_product(document: dict | None) -> Product | None:
    if not document:
        return None
    return Product(
        sku=document["sku"],
        name=document["name"],
        description=document.get("description", ""),
        price=float(document["price"]),
        stock=int(document.get("stock", 0)),
        is_active=bool(document.get("is_active", True)),
        created_at=document.get("created_at"),
    )


def _serialize_movement(movement: StockMovement) -> dict:
    return {
        "product_sku": movement.product_sku,
        "movement_type": movement.movement_type.value,
        "quantity": movement.quantity,
        "reason": movement.reason,
        "created_at": movement.created_at,
    }


def _deserialize_movement(document: dict) -> StockMovement:
    return StockMovement(
        product_sku=document["product_sku"],
        movement_type=MovementType(document["movement_type"]),
        quantity=int(document["quantity"]),
        reason=document["reason"],
        created_at=document["created_at"],
    )


def _serialize_sale(sale: Sale) -> dict:
    return {
        "product_sku": sale.product_sku,
        "product_name": sale.product_name,
        "unit_price": sale.unit_price,
        "quantity": sale.quantity,
        "total": sale.total,
        "created_at": sale.created_at,
    }


def _deserialize_sale(document: dict) -> Sale:
    return Sale(
        product_sku=document["product_sku"],
        product_name=document["product_name"],
        unit_price=float(document["unit_price"]),
        quantity=int(document["quantity"]),
        total=float(document["total"]),
        created_at=document["created_at"],
    )


class MongoProductRepository(ProductRepository):
    def __init__(self, database: Database) -> None:
        self.collection = database.products

    def add(self, product: Product) -> None:
        self.collection.insert_one(_serialize_product(product))

    def get_by_sku(self, sku: str) -> Product | None:
        document = self.collection.find_one({"sku": sku.strip().upper()})
        return _deserialize_product(document)

    def list_all(self) -> list[Product]:
        return [
            _deserialize_product(document)
            for document in self.collection.find().sort("created_at", DESCENDING)
        ]

    def list_active(self) -> list[Product]:
        return [
            _deserialize_product(document)
            for document in self.collection.find({"is_active": True}).sort("created_at", DESCENDING)
        ]

    def update(self, product: Product) -> None:
        self.collection.update_one({"sku": product.sku}, {"$set": _serialize_product(product)})


class MongoMovementRepository(MovementRepository):
    def __init__(self, database: Database) -> None:
        self.collection = database.stock_movements

    def add(self, movement: StockMovement) -> None:
        self.collection.insert_one(_serialize_movement(movement))

    def list_by_product(self, sku: str) -> list[StockMovement]:
        return [
            _deserialize_movement(document)
            for document in self.collection.find({"product_sku": sku.strip().upper()}).sort(
                "created_at", DESCENDING
            )
        ]

    def list_recent(self, limit: int = 10) -> list[StockMovement]:
        return [
            _deserialize_movement(document)
            for document in self.collection.find().sort("created_at", DESCENDING).limit(limit)
        ]


class MongoSaleRepository(SaleRepository):
    def __init__(self, database: Database) -> None:
        self.collection = database.sales

    def add(self, sale: Sale) -> None:
        self.collection.insert_one(_serialize_sale(sale))

    def list_recent(self, limit: int = 10) -> list[Sale]:
        return [
            _deserialize_sale(document)
            for document in self.collection.find().sort("created_at", DESCENDING).limit(limit)
        ]

    def list_by_date(self, day: date) -> list[Sale]:
        start = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
        end = datetime.combine(day, time.max).replace(tzinfo=timezone.utc)
        return [
            _deserialize_sale(document)
            for document in self.collection.find(
                {"created_at": {"$gte": start, "$lte": end}}
            ).sort("created_at", DESCENDING)
        ]
