from django.shortcuts import get_object_or_404
from ...models.customer import Customer
from ...models.wishlist import Wishlist
from ...models.product import Product


def get_or_create_customer(user):
    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": user.username
        }
    )

    return customer

def get_data_wishlist_service(user):

    customer = get_or_create_customer(user)

    wishlist_items = Wishlist.objects.filter(
        customer=customer
    ).select_related('product').order_by('-created_at')

    return wishlist_items

def add_wishlist_service(user, product_id):

    customer = get_or_create_customer(user)

    product = get_object_or_404(
        Product,
        id=product_id,
        status=True,
        category__status=True
    )


    wishlist, created = Wishlist.objects.get_or_create(
        customer = customer,
        product = product
    )

    return wishlist, created

def remove_wishlist_service(user, product_id):

    customer = get_or_create_customer(user)

    Wishlist.objects.filter(
        customer = customer,
        product_id = product_id
    ).delete()


