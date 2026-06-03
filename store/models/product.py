from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal

from .category import Category

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    product_image = models.ImageField(upload_to='products/', null=True, blank=True)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    quantity = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    status = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    entered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
    
    @property
    def sale_price(self):
        discount_rate = Decimal(self.discount) / Decimal("100")
        return self.price - (self.price * discount_rate)


