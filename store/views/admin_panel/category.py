from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from store.decorators import admin_required

from store.services.admin_panel.category import (
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
        "store/admin_panel/categories/list.html",
        context
    )


@admin_required
def add_category(request):

    if request.method == "POST":

        try:
            create_category_service(
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
                "store/admin_panel/categories/add.html"
            )

        messages.success(
            request,
            "Thêm danh mục thành công"
        )

        return redirect("admin_category")

    return render(
        request,
        "store/admin_panel/categories/add.html"
    )


@admin_required
def edit_category(request, category_id):
    context = get_category_detail_service(
        category_id
    )

    if request.method == "POST":

        try:
            update_category_service(
                category_id,
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
                "store/admin_panel/categories/edit.html",
                context
            )

        messages.success(
            request,
            "Cập nhật danh mục thành công"
        )

        return redirect("admin_category")

    return render(
        request,
        "store/admin_panel/categories/edit.html",
        context
    )


@admin_required
def delete_category(request, category_id):

    delete_category_service(
        category_id
    )

    return redirect("admin_category")


