from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from store.models.product import Product
from store.models.category import Category


def clean_decimal(value, field_name):
    if value in [None, ""]:
        raise ValidationError(f"{field_name} không được để trống")

    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValidationError(f"{field_name} không hợp lệ")

    if number < 0:
        raise ValidationError(f"{field_name} không được âm")

    return number


def clean_int(value, field_name, minimum=0, maximum=None):
    if value in [None, ""]:
        raise ValidationError(f"{field_name} không được để trống")

    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} không hợp lệ")

    if number < minimum:
        raise ValidationError(f"{field_name} phải lớn hơn hoặc bằng {minimum}")

    if maximum is not None and number > maximum:
        raise ValidationError(f"{field_name} không được lớn hơn {maximum}")

    return number


def clean_product_payload(data):
    product_name = data.get("product_name", "").strip()

    if not product_name:
        raise ValidationError("Tên sản phẩm không được để trống")

    category_id = data.get("category")

    if not category_id:
        raise ValidationError("Vui lòng chọn danh mục")

    category = get_object_or_404(
        Category,
        id=category_id
    )

    return {
        "product_name": product_name,
        "description": data.get("description", "").strip(),
        "price": clean_decimal(data.get("price"), "Giá sản phẩm"),
        "discount": clean_int(
            data.get("discount", 0),
            "Giảm giá",
            minimum=0,
            maximum=100
        ),
        "quantity": clean_int(
            data.get("quantity", 0),
            "Số lượng",
            minimum=0
        ),
        "category": category,
    }


def get_admin_products_service():

    products = Product.objects.all().order_by(
        "-id"
    )

    return {
        "products": products
    }


def get_add_product_data_service():

    categories = Category.objects.all()

    return {
        "categories": categories
    }


def create_product_service(data, files):
    cleaned_data = clean_product_payload(data)

    product = Product(
        product_name=cleaned_data["product_name"],
        description=cleaned_data["description"],
        price=cleaned_data["price"],
        discount=cleaned_data["discount"],
        quantity=cleaned_data["quantity"],
        category=cleaned_data["category"],
        product_image=files.get("product_image")
    )

    product.full_clean()
    product.save()

    return product


def get_edit_product_data_service(product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    categories = Category.objects.all()

    return {
        "product": product,
        "categories": categories
    }


def update_product_service(product_id, data, files):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    cleaned_data = clean_product_payload(data)

    product.product_name = cleaned_data["product_name"]
    product.description = cleaned_data["description"]
    product.price = cleaned_data["price"]
    product.discount = cleaned_data["discount"]
    product.quantity = cleaned_data["quantity"]
    product.category = cleaned_data["category"]

    if files.get("product_image"):
        product.product_image = files.get(
            "product_image"
        )

    product.full_clean()
    product.save()

    return product


def delete_product_service(product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    product.delete()


