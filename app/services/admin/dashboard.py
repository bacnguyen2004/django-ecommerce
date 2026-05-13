from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.category import Category


def get_dashboard_data_service():

    total_products = Product.objects.count()

    total_categories = Category.objects.count()

    total_customers = Customer.objects.count()

    total_orders = Order.objects.filter(
        complete=True
    ).count()

    completed_orders = Order.objects.filter(
        complete=True,
        status="completed"
    )

    revenue = sum(
        order.total_price
        for order in completed_orders
    )

    recent_orders = Order.objects.filter(
        complete=True
    ).order_by(
        "-created_at"
    )[:5]

    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "revenue": revenue,
        "recent_orders": recent_orders,
    }