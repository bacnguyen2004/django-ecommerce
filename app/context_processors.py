from .models.category import Category
from .models.customer import Customer
from .models.order import Order
from .models.wishlist import Wishlist


def global_data(request):
    categories = Category.objects.filter(status=True)
    totalItem = 0
    totalSave = 0

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(
            user=request.user
        )

        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )

        totalItem = order.total_items
        totalSave = Wishlist.objects.filter(customer=customer).count()

    return {
        'categories': categories,
        'totalItem': totalItem,
        'totalSave': totalSave,
    }
