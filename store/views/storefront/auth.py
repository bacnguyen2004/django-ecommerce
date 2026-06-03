from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout

from store.services.storefront.auth import (
    register_user_service,
    login_user_service
)


def register_user(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        result = register_user_service(
            email=request.POST.get("email"),
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            confirm_password=request.POST.get(
                "confirm_password"
            )
        )

        if not result["success"]:
            messages.error(
                request,
                result["message"]
            )
            return redirect("register")

        messages.success(
            request,
            "Đăng ký thành công! Vui lòng đăng nhập."
        )

        return redirect("login")

    return render(
        request,
        "store/storefront/auth/register.html"
    )


def login_page(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        result = login_user_service(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if not result["success"]:
            messages.error(
                request,
                result["message"]
            )
            return redirect("login")

        login(
            request,
            result["user"]
        )

        return redirect("home")

    return render(
        request,
        "store/storefront/auth/login.html"
    )


def logout_user(request):

    logout(request)

    return redirect("login")

