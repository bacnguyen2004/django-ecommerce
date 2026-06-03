from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from store.models.customer import Customer
from store.models.order import Order


def get_admin_customers_service():

    customers = Customer.objects.all().order_by(
        "-id"
    )

    return {
        "customers": customers
    }


def get_customer_detail_service(customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    orders = Order.objects.filter(
        customer=customer,
        complete=True
    ).order_by(
        "-created_at"
    )

    return {
        "customer": customer,
        "orders": orders
    }


def get_edit_customer_service(customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    return {
        "customer": customer
    }


def update_customer_service(customer_id, data):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    role = data.get("role")

    valid_roles = {
        choice[0]
        for choice in Customer.ROLE_CHOICES
    }

    if role not in valid_roles:
        raise ValidationError("Vai trò khách hàng không hợp lệ")

    customer.name = data.get(
        "name",
        ""
    ).strip()

    customer.phone = data.get(
        "phone",
        ""
    ).strip()

    customer.role = role

    customer.status = data.get(
        "status"
    ) == "on"

    customer.save()

    return customer


def toggle_customer_status_service(customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    customer.status = not customer.status

    customer.save(
        update_fields=[
            "status"
        ]
    )

    return customer


