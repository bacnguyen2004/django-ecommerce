from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from store.api.views import (
    products_api,
    product_detail_api,
    category_api,
    register_api,
    profile_api,
    my_orders_api,
    orders_api,
    order_detail_api,
    admin_order_detail_api,
    cancel_order_api,
    CustomerTokenObtainPairView,
)


urlpatterns = [
    path("products/", products_api, name="products_api"),

    path(
        "products/<int:id>/",
        product_detail_api,
        name="product_detail_api"
    ),

    path("categories/", category_api, name="categories_api"),

    path(
        "auth/register/",
        register_api,
        name="register_api"
    ),

    path(
        "auth/login/",
        CustomerTokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    path("auth/profile/", profile_api, name="profile_api"),

    path("my-orders/", my_orders_api, name="my_orders_api"),
    path("orders/", orders_api, name="orders_api"),
    path(
        "orders/<int:id>/",
        admin_order_detail_api,
        name="admin_order_detail_api"
    ),
    path(
        "my-orders/<int:id>/",
        order_detail_api,
        name="order_detail_api"
    ),
    path(
        "my-orders/<int:id>/cancel/",
        cancel_order_api,
        name="cancel_order_api"
    ),
]


