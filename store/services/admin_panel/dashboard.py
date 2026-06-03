from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from store.models.category import Category
from store.models.customer import Customer
from store.models.order import Order, OrderItem
from store.models.product import Product


LOW_STOCK_THRESHOLD = 10


def _line_total_expression():
    return ExpressionWrapper(
        F("price") * F("quantity"),
        output_field=DecimalField(max_digits=14, decimal_places=2)
    )


def _money_or_zero(value):
    return value if value is not None else Decimal("0")


def _get_revenue_chart_data():
    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    daily_revenue = (
        OrderItem.objects.filter(
            order__complete=True,
            order__status="completed",
            order__created_at__date__gte=start_date
        )
        .annotate(day=TruncDate("order__created_at"))
        .values("day")
        .annotate(total=Sum(_line_total_expression()))
        .order_by("day")
    )

    revenue_by_day = {
        item["day"]: _money_or_zero(item["total"])
        for item in daily_revenue
    }

    days = [
        start_date + timedelta(days=offset)
        for offset in range(7)
    ]

    labels = [
        day.strftime("%d/%m")
        for day in days
    ]
    values = [
        int(revenue_by_day.get(day, Decimal("0")))
        for day in days
    ]
    max_value = max(values) if values else 0

    return {
        "labels": labels,
        "values": values,
        "points": [
            {
                "label": label,
                "value": value,
                "percent": round((value / max_value) * 100)
                if max_value
                else 0,
            }
            for label, value in zip(labels, values)
        ],
        "has_data": any(values),
    }


def _get_order_status_counts():
    status_rows = (
        Order.objects.filter(complete=True)
        .values("status")
        .annotate(total=Count("id"))
    )

    status_counts = {
        choice[0]: 0
        for choice in Order.ORDER_STATUS_CHOICES
    }

    status_counts.update({
        row["status"]: row["total"]
        for row in status_rows
    })

    return status_counts


def _get_recent_activities(recent_orders, low_stock_count):
    activities = []

    status_colors = {
        "pending": "orange",
        "confirmed": "blue",
        "shipping": "purple",
        "completed": "green",
        "cancelled": "red",
    }

    for order in recent_orders[:3]:
        customer_name = (
            order.customer.name
            if order.customer and order.customer.name
            else "Khách lẻ"
        )
        activities.append({
            "title": f"Đơn hàng #{order.id}",
            "description": f"{customer_name} - {order.get_status_display()}",
            "color": status_colors.get(order.status, "blue"),
        })

    if low_stock_count:
        activities.append({
            "title": "Cảnh báo tồn kho",
            "description": f"{low_stock_count} sản phẩm cần nhập thêm",
            "color": "orange",
        })

    if not activities:
        activities.append({
            "title": "Chưa có hoạt động mới",
            "description": "Hệ thống sẽ hiển thị khi có đơn hàng hoặc cảnh báo.",
            "color": "blue",
        })

    return activities[:4]


def get_dashboard_data_service():

    total_products = Product.objects.filter(
        status=True
    ).count()

    total_categories = Category.objects.filter(
        status=True
    ).count()

    total_customers = Customer.objects.filter(
        role="customer"
    ).count()

    total_orders = Order.objects.filter(
        complete=True
    ).count()

    status_counts = _get_order_status_counts()

    completed_orders = status_counts["completed"]

    revenue = _money_or_zero(
        OrderItem.objects.filter(
            order__complete=True,
            order__status="completed"
        ).aggregate(
            total=Sum(_line_total_expression())
        )["total"]
    )

    completion_rate = (
        round((completed_orders / total_orders) * 100)
        if total_orders
        else 0
    )

    low_stock_count = Product.objects.filter(
        status=True,
        quantity__lte=LOW_STOCK_THRESHOLD
    ).count()

    low_stock_products = Product.objects.filter(
        status=True,
        quantity__lte=LOW_STOCK_THRESHOLD
    ).select_related(
        "category"
    ).order_by(
        "quantity",
        "product_name"
    )[:5]

    recent_orders = Order.objects.filter(
        complete=True
    ).select_related(
        "customer"
    ).order_by(
        "-created_at"
    )[:5]

    top_products = (
        OrderItem.objects.filter(
            order__complete=True,
            order__status="completed",
            product__isnull=False
        )
        .values(
            "product_id",
            "product__product_name"
        )
        .annotate(
            sold=Sum("quantity"),
            revenue=Sum(_line_total_expression())
        )
        .order_by("-sold")[:5]
    )

    revenue_chart = _get_revenue_chart_data()

    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "pending_orders": status_counts["pending"],
        "confirmed_orders": status_counts["confirmed"],
        "shipping_orders": status_counts["shipping"],
        "completed_orders": completed_orders,
        "cancelled_orders": status_counts["cancelled"],
        "completion_rate": completion_rate,
        "low_stock_count": low_stock_count,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
        "low_stock_products": low_stock_products,
        "top_products": top_products,
        "revenue": revenue,
        "revenue_chart_labels": revenue_chart["labels"],
        "revenue_chart_values": revenue_chart["values"],
        "revenue_chart_points": revenue_chart["points"],
        "revenue_chart_has_data": revenue_chart["has_data"],
        "recent_activities": _get_recent_activities(
            list(recent_orders),
            low_stock_count
        ),
        "recent_orders": recent_orders,
    }
