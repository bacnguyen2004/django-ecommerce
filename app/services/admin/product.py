from django.shortcuts import get_object_or_404

from app.models.product import Product
from app.models.category import Category


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

    category = get_object_or_404(
        Category,
        id=data.get("category")
    )

    Product.objects.create(
        product_name=data.get("product_name"),
        description=data.get("description"),
        price=data.get("price"),
        discount=data.get("discount"),
        quantity=data.get("quantity"),
        category=category,
        product_image=files.get("product_image")
    )


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

    product.product_name = data.get(
        "product_name"
    )

    product.description = data.get(
        "description"
    )

    product.price = data.get(
        "price"
    )

    product.discount = data.get(
        "discount"
    )

    product.quantity = data.get(
        "quantity"
    )

    category = get_object_or_404(
        Category,
        id=data.get("category")
    )

    product.category = category

    if files.get("product_image"):
        product.product_image = files.get(
            "product_image"
        )

    product.save()


def delete_product_service(product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    product.delete()