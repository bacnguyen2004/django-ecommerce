from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from store.models.product import Product


def clean_price(value, field_name):
    if value in [None, ""]:
        return None

    try:
        price = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValidationError({
            field_name: "Giá không hợp lệ"
        })

    if price < 0:
        raise ValidationError({
            field_name: "Giá không được âm"
        })

    return price


def get_products(
    search=None,
    category=None,
    min_price=None,
    max_price=None,
):
    min_price = clean_price(min_price, "min_price")
    max_price = clean_price(max_price, "max_price")

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise ValidationError({
            "max_price": "Giá tối đa phải lớn hơn hoặc bằng giá tối thiểu"
        })

    products = Product.objects.filter(
        status=True,
        category__status=True
    )

    search = (search or "").strip()

    if search:
        products = products.filter(
            Q(product_name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__category_name__icontains=search)
        )

    if category:
        try:
            category = int(category)
        except (TypeError, ValueError):
            raise ValidationError({
                "category": "Danh mục không hợp lệ"
            })

        products = products.filter(
            category_id=category
        )

    if min_price:
        products = products.filter(
            price__gte=min_price
        )

    if max_price:
        products = products.filter(
            price__lte=max_price
        )

    return products.order_by("-id")

def get_product_by_id(id):

    return get_object_or_404(
        Product,
        status=True,
        id=id,
        category__status=True
    )



