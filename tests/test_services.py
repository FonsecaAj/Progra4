from __future__ import annotations

import pytest

from app.domain.exceptions import DuplicateSKUError, InactiveProductError, InsufficientStockError


def test_create_product_success(service_container):
    product = service_container.product_service.create_product(
        sku="abc-1",
        name="Café Molido",
        description="Bolsa de 500 gramos",
        price=12.5,
        stock=8,
    )

    assert product.sku == "ABC-1"
    assert product.stock == 8


def test_reject_duplicate_sku(service_container):
    service_container.product_service.create_product(
        sku="abc-1",
        name="Café Molido",
        description="Bolsa de 500 gramos",
        price=12.5,
        stock=8,
    )

    with pytest.raises(DuplicateSKUError):
        service_container.product_service.create_product(
            sku="ABC-1",
            name="Otro Café",
            description="Duplicado",
            price=11.0,
            stock=1,
        )


def test_inventory_entry_and_exit(service_container):
    service_container.product_service.create_product(
        sku="abc-2",
        name="Té Negro",
        description="Caja de 20 sobres",
        price=7.2,
        stock=10,
    )

    service_container.inventory_service.record_entry("abc-2", 5, "Compra semanal")
    product = service_container.product_service.get_product("abc-2")
    assert product.stock == 15

    service_container.inventory_service.record_exit("abc-2", 3, "Ajuste de vitrina")
    product = service_container.product_service.get_product("abc-2")
    assert product.stock == 12


def test_reject_exit_without_stock(service_container):
    service_container.product_service.create_product(
        sku="abc-3",
        name="Miel",
        description="Frasco pequeño",
        price=9.4,
        stock=2,
    )

    with pytest.raises(InsufficientStockError):
        service_container.inventory_service.record_exit("abc-3", 5, "Salida inválida")


def test_register_sale_updates_stock_and_movements(service_container):
    service_container.product_service.create_product(
        sku="abc-4",
        name="Galletas",
        description="Paquete surtido",
        price=4.0,
        stock=7,
    )

    sale = service_container.sales_service.register_sale("abc-4", 2)
    product = service_container.product_service.get_product("abc-4")
    history = service_container.inventory_service.list_product_history("abc-4")

    assert sale.total == 8.0
    assert product.stock == 5
    assert history[0].movement_type.value == "SALE"


def test_reject_sale_for_inactive_product(service_container):
    service_container.product_service.create_product(
        sku="abc-5",
        name="Granola",
        description="Pack saludable",
        price=5.5,
        stock=6,
        is_active=False,
    )

    with pytest.raises(InactiveProductError):
        service_container.sales_service.register_sale("abc-5", 1)
