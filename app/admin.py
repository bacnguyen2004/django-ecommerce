from django.contrib import admin

from .models.product import Product
from .models.customer import Customer
from .models.category import Category
from .models.order import Order, OrderItem, ShippingAddress
from .models.wishlist import Wishlist
from .models.payment import Payment


admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Wishlist)
admin.site.register(Payment)