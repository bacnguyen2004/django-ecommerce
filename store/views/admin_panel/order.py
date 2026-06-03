from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from store.decorators import admin_required

from store.services.admin_panel.order import (
    get_admin_orders_service,
    get_admin_order_detail_service,
    update_order_status_service
)


@admin_required
def admin_order(request):

    context = get_admin_orders_service()

    return render(
        request,
        "store/admin_panel/orders/list.html",
        context
    )


@admin_required
def admin_order_detail(request, order_id):

    context = get_admin_order_detail_service(
        order_id
    )

    return render(
        request,
        "store/admin_panel/orders/detail.html",
        context
    )


@admin_required
def update_order_status(request, order_id):

    if request.method == "POST":

        status = request.POST.get(
            "status"
        )

        try:
            order = update_order_status_service(
                order_id,
                status
            )

        except ValidationError as exc:
            messages.error(
                request,
                exc.messages[0]
            )

            return redirect(
                "admin_order_detail",
                order_id=order_id
            )

        messages.success(
            request,
            "Cập nhật trạng thái đơn hàng thành công"
        )

        return redirect(
            "admin_order_detail",
            order_id=order.id
        )

    return redirect("admin_order")


