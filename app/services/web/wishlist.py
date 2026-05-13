from django.shortcuts import get_object_or_404
from ...models.wishlist import Wishlist
from ...models.product import Product

def get_data_wishlist_service(user):

    customer = user.customer

    wishlist_items = Wishlist.objects.filter(
        customer=customer
    ).select_related('product').order_by('-created_at')

    return wishlist_items

def add_wishlist_service(user, product_id):

    customer = user.customer

    product = get_object_or_404(
        Product,
        id=product_id
    )


    Wishlist.objects.create(
        customer = customer,
        product = product
    )

def remove_wishlist_service(user, product_id):

    customer = user.customer

    Wishlist.objects.filter(
        customer = customer,
        product_id = product_id
    ).delete()
