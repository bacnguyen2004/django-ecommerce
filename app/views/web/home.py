from django.shortcuts import render

from app.services.web.home import (
    get_home_data_service
)


def home(request):

    context = get_home_data_service(
        request.user
    )

    return render(
        request,
        "app/web/home/index.html",
        context
    )


def contact(request):

    return render(
        request,
        "app/web/contact/index.html"
    )