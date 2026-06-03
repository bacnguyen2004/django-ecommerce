from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from store.models.customer import Customer


def register_user(data):
    username = data["username"].strip()
    email = data.get("email", "").strip()

    user = User.objects.create_user(
        username=username,
        email=email,
        password=data["password"]
    )

    Customer.objects.create(
        user=user,
        role="customer"
    )

    return user


def login_user(username, password):

    user = authenticate(
        username=(username or "").strip(),
        password=password
    )

    if not user:
        return None

    customer = getattr(user, "customer", None)

    if customer and not customer.status:
        return None

    return user


