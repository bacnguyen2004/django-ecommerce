from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from app.services.web.cart import (
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
        "app/web/cart/cart.html",
        context
    )


@login_required
def add_to_cart(request, product_id):

    add_to_cart_service(
        request.user,
        product_id
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

    increase_quantity_service(
        request.user,
        product_id
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
    quantity = int(
        request.POST.get("quantity")
    )

    update_quantity_service(
        request.user,
        product_id,
        quantity
    )

    return redirect("cart")