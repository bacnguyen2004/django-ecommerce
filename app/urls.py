from django.urls import path

from .views.web.auth import (
    register_user,
    login_page,
    logout_user
)

from .views.web.home import home,contact

from .views.web.product import (
    product_list,
    product_detail
)

from .views.web.cart import (
    cart,
    add_to_cart,
    update_quantity,
    increase_quantity,
    decrease_quantity,
    remove_from_cart
)

from .views.web.checkout import (
    checkout,
    vnpay_return,
    vnpay_ipn
)

from .views.web.order import (
    my_orders,
    order_detail
)

from .views.web.profile import (
    profile,
    profile_update,
    change_password
)

from .views.web.wishlist import (
    wishlist,
    add_wishlist,
    remove_wishlist
)

from .views.admin.dashboard import dashboard

from .views.admin.product import (
    admin_products,
    add_product,
    edit_product,
    delete_product
)

from .views.admin.category import (
    admin_category,
    add_category,
    edit_category,
    delete_category
)

from .views.admin.order import (
    admin_order,
    admin_order_detail,
    update_order_status
)

from .views.admin.customer import (
    admin_customer,
    customer_detail,
    edit_customer,
    toggle_customer_status
)

urlpatterns = [
    # WEB
    path('', home, name='home'),
    path('contact/', contact, name='contact'),

    # AUTH
    path('auth/register/', register_user, name='register'),
    path('auth/login/', login_page, name='login'),
    path('auth/logout/', logout_user, name='logout'),

    # PRODUCTS
    path('products/', product_list, name='product_list'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),

    # PROFILE
    path('profile/', profile, name='profile'),
    path('profile/update/', profile_update, name='profile_update'),
    path('profile/change-password/', change_password, name='change_password'),

    # CART
    path('cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', update_quantity, name='update_quantity'),
    path('cart/increase/<int:product_id>/', increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),

    # CHECKOUT
    path('checkout/', checkout, name='checkout'),
    path('vnpay/ipn/', vnpay_ipn, name='vnpay_ipn'),
    path('vnpay/return/', vnpay_return, name='vnpay_return'),

    # ORDERS
    path('orders/', my_orders, name='my_orders'),
    path('orders/<int:id>/', order_detail, name='order_detail'),

    # WISHLIST
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_wishlist, name='add_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_wishlist, name='remove_wishlist'),

    # DASHBOARD
    path('admin-panel/dashboard/', dashboard, name='dashboard'),

    # PRODUCT
    path('admin-panel/products/', admin_products, name='admin_product'),
    path('admin-panel/products/add/', add_product, name='add_product'),
    path('admin-panel/products/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('admin-panel/products/delete/<int:product_id>/', delete_product, name='delete_product'),

    # CATEGORY
    path('admin-panel/categories/', admin_category, name='admin_category'),
    path('admin-panel/categories/add/', add_category, name='add_category'),
    path('admin-panel/categories/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('admin-panel/categories/delete/<int:category_id>/', delete_category, name='delete_category'),

    # ORDER
    path('admin-panel/orders/', admin_order, name='admin_order'),
    path('admin-panel/orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('admin-panel/orders/update/<int:order_id>/', update_order_status, name='update_order_status'),

    # CUSTOMER
    path('admin-panel/customers/', admin_customer, name='admin_customer'),
    path('admin-panel/customers/<int:customer_id>/', customer_detail, name='customer_detail'),
    path('admin-panel/customers/edit/<int:customer_id>/', edit_customer, name='edit_customer'),
    path('admin-panel/customers/toggle/<int:customer_id>/', toggle_customer_status, name='toggle_customer_status'),
    ]