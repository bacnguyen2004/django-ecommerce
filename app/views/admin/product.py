from django.shortcuts import render, redirect

from app.decorators import admin_required

from app.services.admin.product import (
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
        "app/admin/products/list.html",
        context
    )


@admin_required
def add_product(request):

    if request.method == "POST":

        create_product_service(
            request.POST,
            request.FILES
        )

        return redirect("admin_product")

    context = get_add_product_data_service()

    return render(
        request,
        "app/admin/products/add.html",
        context
    )


@admin_required
def edit_product(request, product_id):

    if request.method == "POST":

        update_product_service(
            product_id,
            request.POST,
            request.FILES
        )

        return redirect("admin_product")

    context = get_edit_product_data_service(
        product_id
    )

    return render(
        request,
        "app/admin/products/edit.html",
        context
    )


@admin_required
def delete_product(request, product_id):

    delete_product_service(
        product_id
    )

    return redirect("admin_product")