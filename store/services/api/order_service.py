from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from store.models.order import Order, OrderItem
from store.models.product import Product
from store.models.customer import Customer


def get_customer_for_user(user):
    customer, _created = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": user.username
        }
    )

    return customer


def is_order_admin(user):
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    customer = getattr(user, "customer", None)

    return bool(customer and customer.role == "admin")


def get_my_orders(user):

    customer = get_customer_for_user(user)

    return Order.objects.filter(
        customer=customer,
        complete=True
    ).prefetch_related(
        "orderitem_set__product"
    ).order_by("-id")


def get_my_order_detail(user, order_id):

    customer = get_customer_for_user(user)

    return get_object_or_404(
        Order.objects.prefetch_related("orderitem_set__product"),
        id=order_id,
        customer=customer,
        complete=True
    )


def get_all_orders_for_admin(user):
    if not is_order_admin(user):
        raise PermissionDenied("Chỉ admin mới được xem tất cả đơn hàng")

    return Order.objects.filter(
        complete=True
    ).select_related(
        "customer",
        "customer__user",
    ).prefetch_related(
        "orderitem_set__product"
    ).order_by("-id")


def get_order_detail_for_admin(user, order_id):
    if not is_order_admin(user):
        raise PermissionDenied("Chỉ admin mới được xem chi tiết đơn hàng này")

    return get_object_or_404(
        Order.objects.select_related(
            "customer",
            "customer__user",
        ).prefetch_related(
            "orderitem_set__product"
        ),
        id=order_id,
        complete=True
    )


@transaction.atomic
def create_order(user, products_data):

    if not products_data:
        raise ValidationError(
            "Danh sách sản phẩm không được để trống"
        )

    customer = get_customer_for_user(user)

    order = Order.objects.create(
        customer=customer,
        complete=True,
        status="pending"
    )

    requested_quantities = {}

    for item in products_data:
        quantity = item["quantity"]

        if quantity <= 0:
            raise ValidationError(
                "Số lượng phải lớn hơn 0"
            )

        product_id = item["product_id"]

        requested_quantities[product_id] = (
            requested_quantities.get(product_id, 0) + quantity
        )

    for product_id, quantity in requested_quantities.items():

        try:
            product = Product.objects.select_for_update().get(
                id=product_id,
                status=True,
                category__status=True
            )
        except Product.DoesNotExist:
            raise ValidationError(
                "Sản phẩm không tồn tại hoặc đã ngừng bán"
            )

        updated = Product.objects.filter(
            id=product.id,
            quantity__gte=quantity
        ).update(
            quantity=F("quantity") - quantity
        )

        if not updated:
            raise ValidationError(
                f"{product.product_name} không đủ hàng"
            )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.sale_price,
        )

    return order


@transaction.atomic
def cancel_my_order(user, order_id):
    customer = get_customer_for_user(user)

    order = get_object_or_404(
        Order.objects.select_for_update(),
        id=order_id,
        customer=customer,
        complete=True
    )

    if order.status != "pending":
        raise ValidationError({
            "status": "Chỉ có thể hủy đơn hàng đang chờ xác nhận"
        })

    order_items = OrderItem.objects.select_related("product").filter(
        order=order
    )

    for item in order_items:
        if item.product_id:
            Product.objects.filter(
                id=item.product_id
            ).update(
                quantity=F("quantity") + item.quantity
            )

    order.status = "cancelled"
    order.save(update_fields=["status"])

    return order


