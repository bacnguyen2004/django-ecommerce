from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from store.models.order import Order, OrderItem, ShippingAddress


def get_admin_orders_service():

    orders = Order.objects.filter(
        complete=True
    ).order_by(
        "-created_at"
    )

    return {
        "orders": orders
    }


def get_admin_order_detail_service(order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    order_items = OrderItem.objects.filter(
        order=order
    )

    shipping = ShippingAddress.objects.filter(
        order=order
    ).first()

    return {
        "order": order,
        "order_items": order_items,
        "shipping": shipping,
    }


def update_order_status_service(order_id, status):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    valid_statuses = {
        choice[0]
        for choice in Order.ORDER_STATUS_CHOICES
    }

    if status not in valid_statuses:
        raise ValidationError("Trạng thái đơn hàng không hợp lệ")

    order.status = status

    order.save(
        update_fields=[
            "status"
        ]
    )

    return order


