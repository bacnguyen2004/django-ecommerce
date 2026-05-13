from django.shortcuts import render

from app.services.web.product import (
    get_product_list_service,
    get_product_detail_service
)


def product_list(request):

    context = get_product_list_service(
        request.GET
    )

    return render(
        request,
        "app/web/products/list.html",
        context
    )


def product_detail(request, product_id):

    context = get_product_detail_service(
        product_id
    )

    return render(
        request,
        "app/web/products/detail.html",
        context
    )