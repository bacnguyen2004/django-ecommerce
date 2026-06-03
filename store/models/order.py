from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

from .customer import Customer
from .product import Product

class Order(models.Model):

    ORDER_STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    complete = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @property
    def total_items(self):
        return self.orderitem_set.count()

    @property
    def total_price(self):
        items = self.orderitem_set.all()
        total = sum(
            [item.get_sale_price for item in items],
            Decimal("0")
        )
        return total


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0"))]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name if self.product else "Sản phẩm đã xoá"

    @property
    def get_sale_price(self):
        return self.price * self.quantity

    @property
    def left_quantity(self):
        if self.product:
            return self.product.quantity - self.quantity
        return 0
    
class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


