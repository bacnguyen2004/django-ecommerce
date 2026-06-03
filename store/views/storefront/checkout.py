from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from store.services.storefront.checkout import (
    CheckoutError,
    get_checkout_data_service,
    place_order_service,
    verify_vnpay_data,
    process_vnpay_return,
    process_vnpay_ipn,
)


@login_required
def checkout(request):

    try:
        context = get_checkout_data_service(
            request.user
        )

    except CheckoutError as exc:
        messages.error(
            request,
            str(exc)
        )

        return redirect("cart")

    if request.method == "POST":

        try:
            result = place_order_service(
                request,
                request.POST
            )

            if result["payment_url"]:
                return redirect(
                    result["payment_url"]
                )

            messages.success(
                request,
                "Đặt hàng COD thành công"
            )

            return redirect("my_orders")

        except CheckoutError as exc:
            messages.error(
                request,
                str(exc)
            )

            return redirect("checkout")

    return render(
        request,
        "store/storefront/orders/checkout.html",
        context
    )


def vnpay_return(request):

    input_data = request.GET.dict()

    if not verify_vnpay_data(input_data):
        messages.error(
            request,
            "Chữ ký VNPay không hợp lệ"
        )

        return redirect("cart")

    try:
        payment, order = process_vnpay_return(
            input_data
        )

        messages.success(
            request,
            "Thanh toán VNPay thành công"
        )

        return redirect(
            "order_detail",
            id=order.id
        )

    except CheckoutError as exc:
        messages.error(
            request,
            str(exc)
        )

        return redirect("checkout")


def vnpay_ipn(request):

    input_data = request.GET.dict()

    if not verify_vnpay_data(input_data):
        return JsonResponse({
            "RspCode": "97",
            "Message": "Invalid signature"
        })

    result = process_vnpay_ipn(
        input_data
    )

    return JsonResponse(result)

