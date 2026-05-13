from django.shortcuts import get_object_or_404

from app.models.order import Order, OrderItem, ShippingAddress


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

    order.status = status

    order.save(
        update_fields=[
            "status"
        ]
    )

    return order