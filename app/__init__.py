from __future__ import annotations

from flask import Flask

from app.config import AppConfig
from app.container import ServiceContainer, build_mongo_container
from app.presentation.web import web_bp


def create_app(
    config_override: dict | None = None,
    services: ServiceContainer | None = None,
) -> Flask:
    app = Flask(__name__)

    config = AppConfig.from_env()
    if config_override:
        for key, value in config_override.items():
            if hasattr(config, key):
                setattr(config, key, value)

    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        TESTING=config.TESTING,
    )

    container = services or build_mongo_container(config)
    app.extensions["services"] = container
    app.extensions["app_config"] = config

    @app.template_filter("currency")
    def currency_filter(value: float) -> str:
        return f"${value:,.2f}"

    app.register_blueprint(web_bp)
    return app
