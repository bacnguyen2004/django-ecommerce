from django.shortcuts import render

from store.services.storefront.home import (
    get_home_data_service
)


def home(request):

    context = get_home_data_service(
        request.user
    )

    return render(
        request,
        "store/storefront/home/index.html",
        context
    )


def contact(request):

    return render(
        request,
        "store/storefront/contact/index.html"
    )

