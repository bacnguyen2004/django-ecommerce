from django.shortcuts import render, redirect

from app.decorators import admin_required

from app.services.admin.category import (
    get_admin_categories_service,
    get_category_detail_service,
    create_category_service,
    update_category_service,
    delete_category_service
)


@admin_required
def admin_category(request):

    context = get_admin_categories_service()

    return render(
        request,
        "app/admin/categories/list.html",
        context
    )


@admin_required
def add_category(request):

    if request.method == "POST":

        create_category_service(
            request.POST,
            request.FILES
        )

        return redirect("admin_category")

    return render(
        request,
        "app/admin/categories/add.html"
    )


@admin_required
def edit_category(request, category_id):

    if request.method == "POST":

        update_category_service(
            category_id,
            request.POST,
            request.FILES
        )

        return redirect("admin_category")

    context = get_category_detail_service(
        category_id
    )

    return render(
        request,
        "app/admin/categories/edit.html",
        context
    )


@admin_required
def delete_category(request, category_id):

    delete_category_service(
        category_id
    )

    return redirect("admin_category")