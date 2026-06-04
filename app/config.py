from __future__ import annotations

import os
import secrets
from dataclasses import dataclass


@dataclass
class AppConfig:
    SECRET_KEY: str
    MONGODB_URI: str
    MONGODB_DATABASE: str
    LOW_STOCK_THRESHOLD: int = 5
    TESTING: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            SECRET_KEY=os.getenv("SECRET_KEY", secrets.token_hex(16)),
            MONGODB_URI=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            MONGODB_DATABASE=os.getenv("MONGODB_DATABASE", "inventory_web_demo"),
            LOW_STOCK_THRESHOLD=int(os.getenv("LOW_STOCK_THRESHOLD", "5")),
            TESTING=os.getenv("TESTING", "false").lower() == "true",
        )
