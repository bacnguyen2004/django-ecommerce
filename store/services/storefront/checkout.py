from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from store.models.customer import Customer
from store.models.order import Order, ShippingAddress
from store.models.payment import Payment
from store.models.product import Product
from store.vnpay import build_payment_url, verify_vnpay_signature


class CheckoutError(Exception):
    pass


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR", "127.0.0.1")


def get_or_create_customer(user):
    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            "name": user.username
        }
    )

    return customer


def get_active_order(customer):
    return Order.objects.filter(
        customer=customer,
        complete=False
    ).first()


def validate_checkout_order(order):
    if not order or order.orderitem_set.count() == 0:
        raise CheckoutError("Giỏ hàng của bạn đang trống")

    for item in order.orderitem_set.select_related("product").all():
        if not item.product:
            raise CheckoutError("Có sản phẩm không còn tồn tại")

        if item.quantity > item.product.quantity:
            raise CheckoutError(
                f'Sản phẩm "{item.product.product_name}" không đủ số lượng trong kho'
            )


def get_checkout_data_service(user):
    customer = get_or_create_customer(user)

    order = get_active_order(customer)

    validate_checkout_order(order)

    cart_items = order.orderitem_set.select_related(
        "product",
        "product__category"
    ).all()

    total_cart_qty_sum = sum(
        item.quantity for item in cart_items
    )

    return {
        "order": order,
        "cartItems": cart_items,
        "totalCartQtySum": total_cart_qty_sum,
        "totalPrice": order.total_price,
    }


def save_shipping_address(order, customer, data):
    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    city = data.get("city", "").strip()
    address = data.get("address", "").strip()
    note = data.get("note", "").strip()

    if not full_name or not phone or not city or not address:
        raise CheckoutError("Vui lòng nhập đầy đủ thông tin giao hàng")

    ShippingAddress.objects.update_or_create(
        order=order,
        defaults={
            "customer": customer,
            "full_name": full_name,
            "phone": phone,
            "city": city,
            "address": address,
            "note": note,
        }
    )


def deduct_inventory(order):
    items = order.orderitem_set.select_related(
        "product"
    ).all()

    for item in items:
        product = item.product

        if not product:
            raise CheckoutError("Sản phẩm không còn tồn tại")

        updated = Product.objects.filter(
            id=product.id,
            quantity__gte=item.quantity
        ).update(
            quantity=F("quantity") - item.quantity
        )

        if not updated:
            raise CheckoutError(
                f'Sản phẩm "{product.product_name}" không đủ số lượng trong kho'
            )


def complete_order(order):
    order.complete = True
    order.status = "pending"

    order.save(
        update_fields=[
            "complete",
            "status"
        ]
    )


def process_cod_order(order):
    with transaction.atomic():

        Payment.objects.update_or_create(
            order=order,
            defaults={
                "method": "COD",
                "amount": order.total_price,
                "status": "pending",
            }
        )

        deduct_inventory(order)

        complete_order(order)


def create_vnpay_payment_url(order, request):
    txn_ref = f"{order.id}{timezone.now().strftime('%Y%m%d%H%M%S')}"

    Payment.objects.update_or_create(
        order=order,
        defaults={
            "method": "VNPAY",
            "amount": order.total_price,
            "status": "pending",
            "txn_ref": txn_ref,
        }
    )

    now = timezone.localtime(
        timezone.now()
    )

    expire_time = now + timedelta(
        minutes=15
    )

    vnp_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_Amount": int(order.total_price * 100),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"Thanh toan don hang {order.id}",
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": settings.VNPAY_RETURN_URL,
        "vnp_IpAddr": get_client_ip(request),
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": expire_time.strftime("%Y%m%d%H%M%S"),
    }

    return build_payment_url(
        settings.VNPAY_PAYMENT_URL,
        vnp_params,
        settings.VNPAY_HASH_SECRET_KEY
    )


def place_order_service(request, data):
    user = request.user

    customer = get_or_create_customer(user)

    order = get_active_order(customer)

    validate_checkout_order(order)

    save_shipping_address(
        order,
        customer,
        data
    )

    payment_method = data.get(
        "payment_method",
        ""
    ).strip().upper()

    if payment_method == "COD":

        process_cod_order(order)

        return {
            "payment_url": None,
            "order": order,
        }

    if payment_method == "VNPAY":

        payment_url = create_vnpay_payment_url(
            order,
            request
        )

        return {
            "payment_url": payment_url,
            "order": order,
        }

    raise CheckoutError("Phương thức thanh toán không hợp lệ")


def verify_vnpay_data(input_data):
    return verify_vnpay_signature(
        input_data,
        settings.VNPAY_HASH_SECRET_KEY
    )


def process_success_vnpay_payment(payment, input_data):
    with transaction.atomic():

        payment = Payment.objects.select_for_update().get(
            id=payment.id
        )

        order = Order.objects.select_for_update().get(
            id=payment.order_id
        )

        if payment.status == "success":
            return payment, order

        response_code = input_data.get("vnp_ResponseCode")
        transaction_status = input_data.get("vnp_TransactionStatus")
        transaction_no = input_data.get("vnp_TransactionNo")
        bank_code = input_data.get("vnp_BankCode")

        if response_code != "00" or transaction_status != "00":
            payment.status = "failed"
            payment.response_code = response_code
            payment.transaction_id = transaction_no
            payment.bank_code = bank_code
            payment.raw_response = input_data

            payment.save()

            raise CheckoutError("Thanh toán VNPay thất bại")

        deduct_inventory(order)

        payment.status = "success"
        payment.response_code = response_code
        payment.transaction_id = transaction_no
        payment.bank_code = bank_code
        payment.raw_response = input_data
        payment.paid_at = timezone.now()

        payment.save()

        complete_order(order)

        return payment, order


def process_vnpay_return(input_data):
    txn_ref = input_data.get("vnp_TxnRef")
    vnp_amount = input_data.get("vnp_Amount")

    payment = Payment.objects.filter(
        txn_ref=txn_ref
    ).select_related(
        "order"
    ).first()

    if not payment:
        raise CheckoutError("Không tìm thấy giao dịch thanh toán")

    try:
        callback_amount = Decimal(vnp_amount) / Decimal("100")
    except Exception:
        raise CheckoutError("Số tiền thanh toán không hợp lệ")

    if callback_amount != payment.amount:
        raise CheckoutError("Số tiền thanh toán không khớp")

    return process_success_vnpay_payment(
        payment,
        input_data
    )


def process_vnpay_ipn(input_data):
    txn_ref = input_data.get("vnp_TxnRef")
    vnp_amount = input_data.get("vnp_Amount")

    payment = Payment.objects.filter(
        txn_ref=txn_ref
    ).select_related(
        "order"
    ).first()

    if not payment:
        return {
            "RspCode": "01",
            "Message": "Order not found"
        }

    try:
        callback_amount = Decimal(vnp_amount) / Decimal("100")
    except Exception:
        return {
            "RspCode": "04",
            "Message": "Invalid amount"
        }

    if callback_amount != payment.amount:
        return {
            "RspCode": "04",
            "Message": "Invalid amount"
        }

    try:
        process_success_vnpay_payment(
            payment,
            input_data
        )

    except CheckoutError as exc:
        return {
            "RspCode": "04",
            "Message": str(exc)
        }

    return {
        "RspCode": "00",
        "Message": "Confirm Success"
    }

