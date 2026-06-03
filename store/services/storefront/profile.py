from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from store.models.customer import Customer


def get_profile_service(user):

    customer, created = Customer.objects.get_or_create(
        user=user
    )

    return {
        "customer": customer
    }


def update_profile_service(user, data):

    customer, created = Customer.objects.get_or_create(
        user=user
    )

    email = data.get(
        "email",
        ""
    ).strip()

    if email and User.objects.filter(email=email).exclude(id=user.id).exists():
        return {
            "success": False,
            "message": "Email đã được sử dụng bởi tài khoản khác."
        }

    user.email = email

    user.save()

    customer.name = data.get(
        "name",
        ""
    ).strip()

    customer.phone = data.get(
        "phone",
        ""
    ).strip()

    customer.save()

    return {
        "success": True,
        "message": "Cập nhật thông tin thành công!"
    }


def change_password_service(request, data):

    user = request.user

    current_password = data.get(
        "currentPassword"
    )

    new_password = data.get(
        "newPassword"
    )

    confirm_password = data.get(
        "confirmPassword"
    )

    if not user.check_password(current_password):
        return {
            "success": False,
            "message": "Mật khẩu hiện tại không đúng."
        }

    if new_password != confirm_password:
        return {
            "success": False,
            "message": "Mật khẩu mới không khớp."
        }

    try:
        validate_password(new_password, user)
    except ValidationError as exc:
        return {
            "success": False,
            "message": exc.messages[0]
        }

    user.set_password(new_password)

    user.save()

    update_session_auth_hash(
        request,
        user
    )

    return {
        "success": True,
        "message": "Đổi mật khẩu thành công."
    }


