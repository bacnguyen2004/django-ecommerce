from django.db.models import Count, Q

from store.models.wishlist import Wishlist
from store.models.customer import Customer
from store.models.product import Product
from store.models.category import Category


def get_home_data_service(user):

    categories = Category.objects.filter(
        status=True
    ).annotate(
        active_product_count=Count(
            "product",
            filter=Q(product__status=True)
        )
    )

    wishlist_product_ids = []

    if user.is_authenticated:
        try:
            customer = Customer.objects.get(
                user=user
            )

            wishlist_product_ids = Wishlist.objects.filter(
                customer=customer
            ).values_list(
                "product_id",
                flat=True
            )

        except Customer.DoesNotExist:
            wishlist_product_ids = []

    new_products = Product.objects.filter(
        status=True,
        category__status=True
    ).order_by(
        "-entered_date"
    )[:10]

    discount_products = Product.objects.filter(
        status=True,
        category__status=True,
        discount__gt=0
    ).order_by(
        "-discount"
    )[:10]

    featured_products = Product.objects.filter(
        status=True,
        category__status=True
    ).order_by(
        "-discount",
        "-entered_date"
    )[:10]

    return {
        "categories": categories,
        "newProducts": new_products,
        "discountProducts": discount_products,
        "featuredProducts": featured_products,
        "wishlist_product_ids": wishlist_product_ids,
    }


