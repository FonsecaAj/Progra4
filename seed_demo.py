from app import create_app


def main() -> None:
    app = create_app()
    services = app.extensions["services"]
    existing_products = services.product_service.list_products()

    if existing_products:
        print("La base ya contiene productos. No se cargaron datos duplicados.")
        return

    sample_products = [
        {
            "sku": "COF-01",
            "name": "Cafe de Altura",
            "description": "Bolsa premium de 340 gramos.",
            "price": 13.5,
            "stock": 16,
        },
        {
            "sku": "TEA-02",
            "name": "Te de Frutas",
            "description": "Caja surtida de infusion.",
            "price": 7.9,
            "stock": 11,
        },
        {
            "sku": "CUP-03",
            "name": "Taza Mercurio",
            "description": "Taza de ceramica para la demo.",
            "price": 9.5,
            "stock": 5,
        },
    ]

    for data in sample_products:
        services.product_service.create_product(**data)

    services.inventory_service.record_entry("COF-01", 4, "Carga inicial de demo")
    services.sales_service.register_sale("COF-01", 2)
    services.sales_service.register_sale("TEA-02", 1)
    print("Datos de ejemplo cargados correctamente.")


if __name__ == "__main__":
    main()
