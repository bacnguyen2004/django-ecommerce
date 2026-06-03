from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from store.services.storefront.profile import (
    get_profile_service,
    update_profile_service,
    change_password_service
)


@login_required
def profile(request):

    context = get_profile_service(
        request.user
    )

    return render(
        request,
        "store/storefront/user/profile.html",
        context
    )


@login_required
def profile_update(request):

    if request.method != "POST":
        return redirect("profile")

    result = update_profile_service(
        request.user,
        request.POST
    )

    if result["success"]:
        messages.success(
            request,
            result["message"]
        )
    else:
        messages.error(
            request,
            result["message"]
        )

    return redirect("profile")


@login_required
def change_password(request):

    if request.method != "POST":
        return redirect("profile")

    result = change_password_service(
        request,
        request.POST
    )

    if result["success"]:
        messages.success(
            request,
            result["message"]
        )
    else:
        messages.error(
            request,
            result["message"]
        )

    return redirect("profile")


