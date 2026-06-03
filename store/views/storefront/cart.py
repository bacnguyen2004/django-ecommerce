from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from store.services.storefront.cart import (
    get_cart_data_service,
    add_to_cart_service,
    remove_from_cart_service,
    increase_quantity_service,
    decrease_quantity_service,
    update_quantity_service
)


@login_required
def cart(request):

    context = get_cart_data_service(
        request.user
    )

    return render(
        request,
        "store/storefront/cart/cart.html",
        context
    )


@login_required
def add_to_cart(request, product_id):

    try:
        add_to_cart_service(
            request.user,
            product_id
        )

        messages.success(
            request,
            "Đã thêm sản phẩm vào giỏ hàng"
        )

    except ValidationError as exc:
        messages.error(
            request,
            exc.messages[0]
        )

    return redirect("cart")


@login_required
def remove_from_cart(request, product_id):

    remove_from_cart_service(
        request.user,
        product_id
    )

    return redirect("cart")


@login_required
def increase_quantity(request, product_id):

    try:
        increase_quantity_service(
            request.user,
            product_id
        )

    except ValidationError as exc:
        messages.error(
            request,
            exc.messages[0]
        )

    return redirect("cart")


@login_required
def decrease_quantity(request, product_id):

    decrease_quantity_service(
        request.user,
        product_id
    )

    return redirect("cart")

@login_required
def update_quantity(request, product_id):
    try:
        quantity = int(
            request.POST.get("quantity", 0)
        )

        update_quantity_service(
            request.user,
            product_id,
            quantity
        )

    except (TypeError, ValueError):
        messages.error(
            request,
            "Số lượng không hợp lệ"
        )

    except ValidationError as exc:
        messages.error(
            request,
            exc.messages[0]
        )

    return redirect("cart")


