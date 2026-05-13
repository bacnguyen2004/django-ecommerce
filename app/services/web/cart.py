from django.shortcuts import get_object_or_404

from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order, OrderItem


def get_or_create_customer(user):

    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": user.username
        }
    )

    return customer


def get_or_create_cart_order(customer):

    order, created = Order.objects.get_or_create(
        customer=customer,
        complete=False
    )

    return order


def get_cart_data_service(user):

    customer = get_or_create_customer(user)

    order = get_or_create_cart_order(customer)

    cart_items = order.orderitem_set.all()

    total_price = sum(
        item.get_sale_price for item in cart_items
    )

    total_cart_qty_sum = sum(
        item.quantity for item in cart_items
    )

    return {
        "cartItems": cart_items,
        "totalPrice": total_price,
        "totalCartQtySum": total_cart_qty_sum,
        "totalItem": order.total_items,
    }


def add_to_cart_service(user, product_id):

    customer = get_or_create_customer(user)

    product = get_object_or_404(
        Product,
        id=product_id
    )

    order = get_or_create_cart_order(customer)

    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            "price": product.sale_price
        }
    )

    if not created:
        order_item.quantity += 1

    order_item.save()

    return order_item


def remove_from_cart_service(user, product_id):

    customer = get_or_create_customer(user)

    order = get_or_create_cart_order(customer)

    item = get_object_or_404(
        OrderItem,
        order=order,
        product_id=product_id
    )

    item.delete()


def increase_quantity_service(user, product_id):

    customer = get_or_create_customer(user)

    order = get_or_create_cart_order(customer)

    item = get_object_or_404(
        OrderItem,
        order=order,
        product_id=product_id
    )

    if item.quantity < item.product.quantity:
        item.quantity += 1
        item.save()

    return item


def decrease_quantity_service(user, product_id):

    customer = get_or_create_customer(user)

    order = get_or_create_cart_order(customer)

    item = get_object_or_404(
        OrderItem,
        order=order,
        product_id=product_id
    )

    item.quantity -= 1

    if item.quantity <= 0:
        item.delete()
    else:
        item.save()

def update_quantity_service(user, product_id,quantity):

    customer = user.customer

    order = get_or_create_cart_order(customer)

    item = get_object_or_404(
        OrderItem,
        order=order,
        product_id=product_id
    )

    if quantity <= 0:
        item.delete()

    elif quantity <= item.product.quantity:

        item.quantity = quantity
        item.save()