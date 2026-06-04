from __future__ import annotations


def seed_basic_data(service_container):
    service_container.product_service.create_product(
        sku="SKU-1",
        name="Chocolate",
        description="Barra premium",
        price=3.5,
        stock=10,
    )
    service_container.product_service.create_product(
        sku="SKU-2",
        name="Taza",
        description="Cerámica blanca",
        price=8.0,
        stock=0,
        is_active=False,
    )


def test_public_catalog_shows_only_active_products(client, service_container):
    seed_basic_data(service_container)

    response = client.get("/")

    assert response.status_code == 200
    assert b"Chocolate" in response.data
    assert b"Taza" not in response.data


def test_create_product_from_form(client):
    response = client.post(
        "/admin/products/new",
        data={
            "sku": "SKU-3",
            "name": "Cafe",
            "description": "Molido",
            "price": "14.25",
            "stock": "12",
            "is_active": "on",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Producto creado correctamente" in response.data
    assert b"SKU-3" in response.data


def test_dashboard_changes_after_sale(client, service_container):
    service_container.product_service.create_product(
        sku="SKU-9",
        name="Filtro",
        description="Repuesto",
        price=6.0,
        stock=4,
    )

    client.post(
        "/admin/sales/new",
        data={"sku": "SKU-9", "quantity": "2"},
        follow_redirects=True,
    )

    response = client.get("/admin")

    assert response.status_code == 200
    assert b"Ventas del d" in response.data
    assert b"Filtro" in response.data
