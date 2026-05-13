from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from app.models.customer import Customer


def register_user_service(
    email,
    username,
    password,
    confirm_password
):

    # Check confirm password
    if password != confirm_password:
        return {
            "success": False,
            "message": "Mật khẩu nhập lại không khớp!"
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

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return {
            "success": False,
            "message": "Tên đăng nhập hoặc mật khẩu không đúng!"
        }

    return {
        "success": True,
        "user": user
    }