from __future__ import annotations

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database


class MongoSession:
    def __init__(self, uri: str, database_name: str) -> None:
        self.client = MongoClient(uri)
        self.database: Database = self.client[database_name]

    def ensure_indexes(self) -> None:
        self.database.products.create_index([("sku", ASCENDING)], unique=True)
        self.database.stock_movements.create_index([("product_sku", ASCENDING), ("created_at", ASCENDING)])
        self.database.sales.create_index([("product_sku", ASCENDING), ("created_at", ASCENDING)])
