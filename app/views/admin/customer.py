from django.shortcuts import render, redirect

from app.decorators import admin_required

from app.services.admin.customer import (
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
        "app/admin/customers/list.html",
        context
    )


@admin_required
def customer_detail(request, customer_id):

    context = get_customer_detail_service(
        customer_id
    )

    return render(
        request,
        "app/admin/customers/detail.html",
        context
    )


@admin_required
def edit_customer(request, customer_id):

    if request.method == "POST":

        update_customer_service(
            customer_id,
            request.POST
        )

        return redirect("admin_customer")

    context = get_edit_customer_service(
        customer_id
    )

    return render(
        request,
        "app/admin/customers/edit.html",
        context
    )


@admin_required
def toggle_customer_status(request, customer_id):

    toggle_customer_status_service(
        customer_id
    )

    return redirect("admin_customer")