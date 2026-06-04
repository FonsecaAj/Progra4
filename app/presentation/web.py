from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.container import ServiceContainer
from app.domain.exceptions import DomainError


web_bp = Blueprint("web", __name__)


def get_services() -> ServiceContainer:
    return current_app.extensions["services"]


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"El campo {field_name} debe ser un número entero.") from exc


def parse_float(value: str, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"El campo {field_name} debe ser un número válido.") from exc


@web_bp.errorhandler(ValueError)
def handle_value_error(error: ValueError):
    flash(str(error), "error")
    return redirect(request.referrer or url_for("web.admin_dashboard"))


@web_bp.errorhandler(DomainError)
def handle_domain_error(error: DomainError):
    flash(str(error), "error")
    return redirect(request.referrer or url_for("web.admin_dashboard"))


@web_bp.route("/health")
def health_check():
    return {"status": "ok"}


@web_bp.route("/")
def public_catalog():
    services = get_services()
    products = services.product_service.list_products(active_only=True)
    return render_template("public/catalog.html", products=products)


@web_bp.route("/admin")
def admin_dashboard():
    services = get_services()
    summary = services.dashboard_service.get_summary()
    products = services.product_service.list_products()
    return render_template("admin/dashboard.html", summary=summary, products=products)


@web_bp.route("/admin/products")
def admin_products():
    services = get_services()
    products = services.product_service.list_products()
    return render_template("admin/products_list.html", products=products)


@web_bp.route("/admin/products/new", methods=["GET", "POST"])
def new_product():
    services = get_services()
    if request.method == "POST":
        try:
            services.product_service.create_product(
                sku=request.form.get("sku", ""),
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                price=parse_float(request.form.get("price"), "precio"),
                stock=parse_int(request.form.get("stock", "0"), "stock"),
                is_active=request.form.get("is_active") == "on",
            )
            flash("Producto creado correctamente.", "success")
            return redirect(url_for("web.admin_products"))
        except ValueError as error:
            flash(str(error), "error")

    return render_template("admin/product_form.html", product=None)


@web_bp.route("/admin/products/<sku>/edit", methods=["GET", "POST"])
def edit_product(sku: str):
    services = get_services()
    product = services.product_service.get_product(sku)

    if request.method == "POST":
        try:
            services.product_service.update_product(
                sku=sku,
                name=request.form.get("name", ""),
                description=request.form.get("description", ""),
                price=parse_float(request.form.get("price"), "precio"),
                is_active=request.form.get("is_active") == "on",
            )
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("web.admin_products"))
        except ValueError as error:
            flash(str(error), "error")

    return render_template("admin/product_form.html", product=product)


@web_bp.route("/admin/inventory/entry", methods=["GET", "POST"])
def inventory_entry():
    return _render_inventory_form(operation="entry")


@web_bp.route("/admin/inventory/exit", methods=["GET", "POST"])
def inventory_exit():
    return _render_inventory_form(operation="exit")


def _render_inventory_form(operation: str):
    services = get_services()
    products = services.product_service.list_products()
    if request.method == "POST":
        sku = request.form.get("sku", "")
        quantity = parse_int(request.form.get("quantity"), "cantidad")
        reason = request.form.get("reason", "")
        try:
            if operation == "entry":
                services.inventory_service.record_entry(sku, quantity, reason)
                flash("Entrada de inventario registrada.", "success")
            else:
                services.inventory_service.record_exit(sku, quantity, reason)
                flash("Salida de inventario registrada.", "success")
            return redirect(url_for("web.admin_dashboard"))
        except DomainError:
            raise

    return render_template(
        "admin/inventory_form.html",
        operation=operation,
        products=products,
    )


@web_bp.route("/admin/sales/new", methods=["GET", "POST"])
def new_sale():
    services = get_services()
    products = services.product_service.list_products(active_only=True)
    if request.method == "POST":
        try:
            sale = services.sales_service.register_sale(
                sku=request.form.get("sku", ""),
                quantity=parse_int(request.form.get("quantity"), "cantidad"),
            )
            flash(
                f"Venta registrada por {sale.quantity} unidad(es) de {sale.product_name}.",
                "success",
            )
            return redirect(url_for("web.admin_dashboard"))
        except ValueError as error:
            flash(str(error), "error")

    return render_template("admin/sales_form.html", products=products)


@web_bp.route("/admin/products/<sku>/history")
def product_history(sku: str):
    services = get_services()
    product = services.product_service.get_product(sku)
    movements = services.inventory_service.list_product_history(sku)
    return render_template(
        "admin/product_history.html",
        product=product,
        movements=movements,
    )
