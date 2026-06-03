from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from store.decorators import admin_required

from store.services.admin_panel.product import (
    get_admin_products_service,
    get_add_product_data_service,
    create_product_service,
    get_edit_product_data_service,
    update_product_service,
    delete_product_service
)


@admin_required
def admin_products(request):

    context = get_admin_products_service()

    return render(
        request,
        "store/admin_panel/products/list.html",
        context
    )


@admin_required
def add_product(request):

    context = get_add_product_data_service()

    if request.method == "POST":

        try:
            create_product_service(
                request.POST,
                request.FILES
            )

        except ValidationError as exc:
            messages.error(
                request,
                exc.messages[0]
            )

            return render(
                request,
                "store/admin_panel/products/add.html",
                context
            )

        messages.success(
            request,
            "Thêm sản phẩm thành công"
        )

        return redirect("admin_product")

    return render(
        request,
        "store/admin_panel/products/add.html",
        context
    )


@admin_required
def edit_product(request, product_id):
    context = get_edit_product_data_service(
        product_id
    )

    if request.method == "POST":

        try:
            update_product_service(
                product_id,
                request.POST,
                request.FILES
            )

        except ValidationError as exc:
            messages.error(
                request,
                exc.messages[0]
            )

            return render(
                request,
                "store/admin_panel/products/edit.html",
                context
            )

        messages.success(
            request,
            "Cập nhật sản phẩm thành công"
        )

        return redirect("admin_product")

    return render(
        request,
        "store/admin_panel/products/edit.html",
        context
    )


@admin_required
def delete_product(request, product_id):

    delete_product_service(
        product_id
    )

    return redirect("admin_product")


