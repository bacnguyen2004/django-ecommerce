from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from app.services.web.order import (
    get_my_orders_service,
    get_order_detail_service
)


@login_required
def my_orders(request):

    context = get_my_orders_service(
        request.user
    )

    return render(
        request,
        "app/web/orders/history.html",
        context
    )


@login_required
def order_detail(request, id):

    context = get_order_detail_service(
        request.user,
        id
    )

    return render(
        request,
        "app/web/orders/detail.html",
        context
    )