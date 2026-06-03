from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from .order import Order

class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Thanh toán khi nhận hàng'),
        ('VNPAY', 'VNPay'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Chờ thanh toán'),
        ('success', 'Thanh toán thành công'),
        ('failed', 'Thanh toán thất bại'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='COD'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))]
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    txn_ref = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True
    )

    transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    response_code = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    bank_code = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    raw_response = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.id}"


