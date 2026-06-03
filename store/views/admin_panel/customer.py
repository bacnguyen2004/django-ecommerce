from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from store.decorators import admin_required

from store.services.admin_panel.customer import (
    get_admin_customers_service,
    get_customer_detail_service,
    get_edit_customer_service,
    update_customer_service,
    toggle_customer_status_service
)


@admin_required
def admin_customer(request):

    context = get_admin_customers_service()

    return render(
        request,
        "store/admin_panel/customers/list.html",
        context
    )


@admin_required
def customer_detail(request, customer_id):

    context = get_customer_detail_service(
        customer_id
    )

    return render(
        request,
        "store/admin_panel/customers/detail.html",
        context
    )


@admin_required
def edit_customer(request, customer_id):
    context = get_edit_customer_service(
        customer_id
    )

    if request.method == "POST":

        try:
            update_customer_service(
                customer_id,
                request.POST
            )

        except ValidationError as exc:
            messages.error(
                request,
                exc.messages[0]
            )

            return render(
                request,
                "store/admin_panel/customers/edit.html",
                context
            )

        messages.success(
            request,
            "Cập nhật khách hàng thành công"
        )

        return redirect("admin_customer")

    return render(
        request,
        "store/admin_panel/customers/edit.html",
        context
    )


@admin_required
def toggle_customer_status(request, customer_id):

    toggle_customer_status_service(
        customer_id
    )

    return redirect("admin_customer")


