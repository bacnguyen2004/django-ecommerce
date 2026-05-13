from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from app.models.product import Product


def get_product_list_service(data):
    keyword = data.get("keyword", "").strip()
    category_id = data.get("category")
    sort = data.get("sort", "newest")

    product_list = Product.objects.filter(
        status=True,
        category__status=True
    )

    if keyword:
        product_list = product_list.filter(
            Q(product_name__icontains=keyword) |
            Q(category__category_name__icontains=keyword)
        )

    if category_id:
        product_list = product_list.filter(category_id=category_id)

    if sort == "price_asc":
        product_list = product_list.order_by("price")
    elif sort == "price_desc":
        product_list = product_list.order_by("-price")
    elif sort == "discount":
        product_list = product_list.filter(discount__gt=0).order_by("-discount")
    else:
        product_list = product_list.order_by("-entered_date")

    paginator = Paginator(product_list, 12)
    products = paginator.get_page(data.get("page"))

    return {
        "products": products,
        "keyword": keyword,
        "category_id": category_id,
        "sort": sort,
    }


def get_product_detail_service(product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        status=True,
        category__status=True
    )

    related_products = Product.objects.filter(
        category=product.category,
        status=True,
        category__status=True
    ).exclude(
        id=product.id
    )[:4]

    return {
        "product": product,
        "relatedProducts": related_products,
    }