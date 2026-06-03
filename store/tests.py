from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models.category import Category
from store.models.customer import Customer
from store.models.order import Order, OrderItem, ShippingAddress
from store.models.payment import Payment
from store.models.product import Product
from store.models.wishlist import Wishlist
from store.services.api.order_service import create_order
from store.services.admin_panel.dashboard import get_dashboard_data_service
from store.services.storefront.auth import login_user_service
from store.services.storefront.cart import add_to_cart_service
from store.services.storefront.checkout import (
    CheckoutError,
    place_order_service,
    process_vnpay_ipn,
    process_vnpay_return,
)
from store.services.storefront.wishlist import add_wishlist_service


class StoreServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="StrongPass123!"
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name="Customer"
        )
        self.category = Category.objects.create(
            category_name="Sách kỹ năng",
            status=True
        )
        self.product = Product.objects.create(
            product_name="Tư duy nhanh và chậm",
            description="Sách tâm lý học",
            price=Decimal("100000"),
            discount=10,
            quantity=2,
            category=self.category,
            status=True
        )
        self.factory = RequestFactory()

    def build_checkout_request(self):
        request = self.factory.post(reverse("checkout"))
        request.user = self.user

        return request

    def create_active_cart_order(self, quantity=1):
        order = Order.objects.create(
            customer=self.customer,
            complete=False,
            status="pending"
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=quantity,
            price=self.product.sale_price
        )

        return order

    def test_cart_cannot_exceed_stock(self):
        add_to_cart_service(self.user, self.product.id)
        add_to_cart_service(self.user, self.product.id)

        with self.assertRaises(DjangoValidationError):
            add_to_cart_service(self.user, self.product.id)

    def test_wishlist_uses_get_or_create(self):
        first_item, first_created = add_wishlist_service(
            self.user,
            self.product.id
        )
        second_item, second_created = add_wishlist_service(
            self.user,
            self.product.id
        )

        self.assertTrue(first_created)
        self.assertFalse(second_created)
        self.assertEqual(first_item.id, second_item.id)
        self.assertEqual(Wishlist.objects.count(), 1)

    def test_locked_customer_cannot_login(self):
        self.customer.status = False
        self.customer.save(update_fields=["status"])

        result = login_user_service(
            "customer",
            "StrongPass123!"
        )

        self.assertFalse(result["success"])

    def test_home_page_uses_general_store_copy(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Chọn nhanh sản phẩm bạn cần"
        )
        self.assertContains(
            response,
            f"?category={self.category.id}"
        )

    def test_product_list_page_renders_product_grid(self):
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tất cả sản phẩm")
        self.assertContains(response, "shop-grid")
        self.assertContains(response, self.product.product_name)

    def test_dashboard_uses_real_order_and_stock_data(self):
        completed_order = Order.objects.create(
            customer=self.customer,
            complete=True,
            status="completed"
        )
        OrderItem.objects.create(
            order=completed_order,
            product=self.product,
            quantity=2,
            price=Decimal("90000.00")
        )
        Order.objects.create(
            customer=self.customer,
            complete=True,
            status="pending"
        )

        data = get_dashboard_data_service()

        self.assertEqual(data["total_orders"], 2)
        self.assertEqual(data["completed_orders"], 1)
        self.assertEqual(data["pending_orders"], 1)
        self.assertEqual(data["completion_rate"], 50)
        self.assertEqual(data["revenue"], Decimal("180000.00"))
        self.assertIn(180000, data["revenue_chart_values"])
        self.assertEqual(data["low_stock_count"], 1)

    def test_checkout_cod_creates_payment_shipping_and_deducts_stock(self):
        order = self.create_active_cart_order(quantity=2)

        result = place_order_service(
            self.build_checkout_request(),
            {
                "full_name": "Customer",
                "phone": "0900000000",
                "city": "Ho Chi Minh",
                "address": "1 Nguyen Trai",
                "payment_method": "COD",
            }
        )

        order.refresh_from_db()
        self.product.refresh_from_db()

        payment = Payment.objects.get(order=order)

        self.assertIsNone(result["payment_url"])
        self.assertTrue(order.complete)
        self.assertEqual(order.status, "pending")
        self.assertEqual(payment.method, "COD")
        self.assertEqual(payment.status, "pending")
        self.assertEqual(self.product.quantity, 0)
        self.assertTrue(
            ShippingAddress.objects.filter(order=order).exists()
        )

    def test_vnpay_return_marks_payment_success_and_completes_order(self):
        order = self.create_active_cart_order(quantity=1)
        payment = Payment.objects.create(
            order=order,
            method="VNPAY",
            amount=order.total_price,
            status="pending",
            txn_ref="txn-001"
        )

        processed_payment, processed_order = process_vnpay_return({
            "vnp_TxnRef": payment.txn_ref,
            "vnp_Amount": str(int(payment.amount * 100)),
            "vnp_ResponseCode": "00",
            "vnp_TransactionStatus": "00",
            "vnp_TransactionNo": "123456",
            "vnp_BankCode": "NCB",
        })

        self.product.refresh_from_db()

        self.assertEqual(processed_payment.status, "success")
        self.assertEqual(processed_payment.transaction_id, "123456")
        self.assertTrue(processed_order.complete)
        self.assertEqual(self.product.quantity, 1)

    def test_vnpay_ipn_rejects_invalid_amount(self):
        order = self.create_active_cart_order(quantity=1)
        payment = Payment.objects.create(
            order=order,
            method="VNPAY",
            amount=order.total_price,
            status="pending",
            txn_ref="txn-002"
        )

        result = process_vnpay_ipn({
            "vnp_TxnRef": payment.txn_ref,
            "vnp_Amount": "1",
            "vnp_ResponseCode": "00",
            "vnp_TransactionStatus": "00",
        })

        order.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(result["RspCode"], "04")
        self.assertFalse(order.complete)
        self.assertEqual(payment.status, "pending")

    def test_admin_dashboard_renders_for_superuser(self):
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!"
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tổng quan quản trị")

    def test_admin_product_list_renders_for_superuser(self):
        admin_user = User.objects.create_superuser(
            username="product_admin",
            email="product-admin@example.com",
            password="StrongPass123!"
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse("admin_product"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Danh sách toàn bộ sản phẩm")
        self.assertContains(response, self.product.product_name)


class StoreApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="apiuser",
            email="apiuser@example.com",
            password="StrongPass123!"
        )
        Customer.objects.create(
            user=self.user,
            name="API User"
        )
        self.category = Category.objects.create(
            category_name="Sách lập trình",
            status=True
        )
        self.product = Product.objects.create(
            product_name="Django thực chiến",
            description="Xây dựng website bán sách",
            price=Decimal("200000"),
            discount=25,
            quantity=5,
            category=self.category,
            status=True
        )

    def authenticate_as(self, username, password="StrongPass123!"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "username": username,
                "password": password
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

        return response

    def test_register_and_login_api_return_jwt(self):
        register_response = self.client.post(
            reverse("register_api"),
            {
                "username": "newapiuser",
                "email": "newapiuser@example.com",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!"
            },
            format="json"
        )

        self.assertEqual(
            register_response.status_code,
            status.HTTP_201_CREATED
        )

        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "username": "newapiuser",
                "password": "StrongPass123!"
            },
            format="json"
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

    def test_product_api_searches_product_name(self):
        response = self.client.get(
            reverse("products_api"),
            {
                "search": "Django"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["product_name"],
            "Django thực chiến"
        )

    def test_product_api_rejects_invalid_price_filter(self):
        response = self.client.get(
            reverse("products_api"),
            {
                "min_price": "abc"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_api_requires_jwt(self):
        response = self.client.post(
            reverse("orders_api"),
            {
                "products": [
                    {
                        "product_id": self.product.id,
                        "quantity": 1
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_api_creates_order_and_deducts_stock(self):
        self.authenticate_as("apiuser")

        response = self.client.post(
            reverse("orders_api"),
            {
                "products": [
                    {
                        "product_id": self.product.id,
                        "quantity": 2
                    }
                ]
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 3)

    def test_user_can_only_view_own_order_detail(self):
        order = create_order(
            user=self.user,
            products_data=[
                {
                    "product_id": self.product.id,
                    "quantity": 1
                }
            ]
        )

        other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="StrongPass123!"
        )
        Customer.objects.create(
            user=other_user,
            name="Other User"
        )

        self.authenticate_as("otheruser")

        response = self.client.get(
            reverse("order_detail_api", kwargs={"id": order.id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_only_admin_can_list_all_orders(self):
        create_order(
            user=self.user,
            products_data=[
                {
                    "product_id": self.product.id,
                    "quantity": 1
                }
            ]
        )

        self.authenticate_as("apiuser")

        customer_response = self.client.get(reverse("orders_api"))

        self.assertEqual(
            customer_response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        admin_user = User.objects.create_superuser(
            username="apiadmin",
            email="apiadmin@example.com",
            password="StrongPass123!"
        )

        self.authenticate_as(admin_user.username)

        admin_response = self.client.get(reverse("orders_api"))

        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(admin_response.data), 1)

    def test_cancel_order_api_marks_cancelled_and_restores_stock(self):
        order = create_order(
            user=self.user,
            products_data=[
                {
                    "product_id": self.product.id,
                    "quantity": 2
                }
            ]
        )

        self.authenticate_as("apiuser")

        response = self.client.post(
            reverse("cancel_order_api", kwargs={"id": order.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(order.status, "cancelled")
        self.assertEqual(self.product.quantity, 5)

    def test_swagger_docs_are_available(self):
        response = self.client.get(reverse("swagger-ui"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order_aggregates_items_and_deducts_stock(self):
        order = create_order(
            user=self.user,
            products_data=[
                {
                    "product_id": self.product.id,
                    "quantity": 2
                },
                {
                    "product_id": self.product.id,
                    "quantity": 1
                },
            ]
        )

        self.product.refresh_from_db()

        item = OrderItem.objects.get(order=order)

        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.price, Decimal("150000.00"))
        self.assertEqual(order.total_price, Decimal("450000.00"))
        self.assertEqual(self.product.quantity, 2)


