from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from store.models.category import Category


def clean_category_name(data):
    category_name = data.get("category_name", "").strip()

    if not category_name:
        raise ValidationError("Tên danh mục không được để trống")

    return category_name


def get_admin_categories_service():

    categories = Category.objects.all().order_by(
        "-id"
    )

    return {
        "categories": categories
    }


def get_category_detail_service(category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )

    return {
        "category": category
    }


def create_category_service(data, files):
    category_name = clean_category_name(data)

    category = Category.objects.create(
        category_name=category_name,
        category_image=files.get("category_image"),
        status=data.get("status") == "on"
    )

    return category


def update_category_service(category_id, data, files):

    category = get_object_or_404(
        Category,
        id=category_id
    )

    category.category_name = clean_category_name(data)

    category.status = data.get(
        "status"
    ) == "on"

    if files.get("category_image"):
        category.category_image = files.get(
            "category_image"
        )

    category.save()


def delete_category_service(category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )

    category.delete()


