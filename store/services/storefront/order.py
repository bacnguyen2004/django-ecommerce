from django.shortcuts import get_object_or_404

from store.models.order import Order, ShippingAddress


def get_my_orders_service(user):

    customer = user.customer

    orders = Order.objects.filter(
        customer=customer,
        complete=True
    ).order_by(
        "-created_at"
    )

    return {
        "orders": orders
    }


def get_order_detail_service(user, order_id):

    customer = user.customer

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=customer
    )

    items = order.orderitem_set.all()

    shipping = ShippingAddress.objects.filter(
        order=order
    ).first()

    return {
        "order": order,
        "items": items,
        "shipping": shipping
    }

