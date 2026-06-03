from rest_framework import serializers

from store.models.product import Product
from store.models.category import Category
from store.models.order import Order,OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class ProductSerializer(serializers.ModelSerializer):
    sale_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Product
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class RegisterSerializer(serializers.Serializer):

    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        data["username"] = data["username"].strip()
        data["email"] = data.get("email", "").strip()

        if not data["username"]:
            raise serializers.ValidationError({
                "username": "Username không được để trống"
            })

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Mật khẩu nhập lại không khớp"
            })

        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError({
                "username": "Username đã tồn tại"
            })

        email = data.get("email")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "email": "Email đã tồn tại"
            })

        try:
            validate_password(data["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({
                "password": exc.messages
            })

        return data


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.product_name", read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        source="get_sale_price",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        source="orderitem_set",
        many=True,
        read_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
    

class OrderItemCreateSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):

    products = OrderItemCreateSerializer(
        many=True
    )

    def validate_products(self, products):
        if not products:
            raise serializers.ValidationError(
                "Danh sách sản phẩm không được để trống"
            )

        return products


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        customer = getattr(self.user, "customer", None)

        if customer and not customer.status:
            raise serializers.ValidationError(
                "Tài khoản của bạn đã bị khóa"
            )

        return data


