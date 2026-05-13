from django.shortcuts import render, redirect

from app.decorators import admin_required

from app.services.admin.order import (
    get_admin_orders_service,
    get_admin_order_detail_service,
    update_order_status_service
)


@admin_required
def admin_order(request):

    context = get_admin_orders_service()

    return render(
        request,
        "app/admin/orders/list.html",
        context
    )


@admin_required
def admin_order_detail(request, order_id):

    context = get_admin_order_detail_service(
        order_id
    )

    return render(
        request,
        "app/admin/orders/detail.html",
        context
    )


@admin_required
def update_order_status(request, order_id):

    if request.method == "POST":

        status = request.POST.get(
            "status"
        )

        order = update_order_status_service(
            order_id,
            status
        )

        return redirect(
            "admin_order_detail",
            order_id=order.id
        )

    return redirect("admin_order")