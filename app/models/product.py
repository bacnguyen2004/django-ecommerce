from django.db import models
from .category import Category

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    product_image = models.ImageField(upload_to='products/', null=True, blank=True)

    price = models.FloatField()
    quantity = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)

    status = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    entered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
    
    @property
    def sale_price(self):
        return self.price - (self.price * self.discount / 100)