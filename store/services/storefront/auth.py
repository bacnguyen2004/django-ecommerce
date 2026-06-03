from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from store.models.customer import Customer


def register_user_service(
    email,
    username,
    password,
    confirm_password
):
    email = (email or "").strip()
    username = (username or "").strip()
    password = password or ""
    confirm_password = confirm_password or ""

    if not username:
        return {
            "success": False,
            "message": "Tên đăng nhập không được để trống!"
        }

    if not email:
        return {
            "success": False,
            "message": "Email không được để trống!"
        }

    if not password:
        return {
            "success": False,
            "message": "Mật khẩu không được để trống!"
        }

    # Check confirm password
    if password != confirm_password:
        return {
            "success": False,
            "message": "Mật khẩu nhập lại không khớp!"
        }

    try:
        validate_password(password)
    except ValidationError as exc:
        return {
            "success": False,
            "message": exc.messages[0]
        }

    # Check username exists
    if User.objects.filter(username=username).exists():
        return {
            "success": False,
            "message": "Tên đăng nhập đã tồn tại!"
        }

    # Check email exists
    if User.objects.filter(email=email).exists():
        return {
            "success": False,
            "message": "Email đã tồn tại!"
        }

    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Create customer profile
    Customer.objects.create(
        user=user
    )

    return {
        "success": True
    }


def login_user_service(username, password):
    username = (username or "").strip()
    password = password or ""

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return {
            "success": False,
            "message": "Tên đăng nhập hoặc mật khẩu không đúng!"
        }

    customer = getattr(user, "customer", None)

    if customer and not customer.status:
        return {
            "success": False,
            "message": "Tài khoản của bạn đã bị khóa!"
        }

    return {
        "success": True,
        "user": user
    }


