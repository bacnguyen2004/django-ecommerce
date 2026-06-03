from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from ...services.storefront.wishlist import (
    get_data_wishlist_service,
    add_wishlist_service,
    remove_wishlist_service
)

@login_required
def wishlist(request):

    wishlist_items = get_data_wishlist_service(request.user)

    context = {
        'wishlist_items': wishlist_items,
    }

    return render(
        request,
        'store/storefront/cart/wishlist.html',
        context
    )

@login_required
def add_wishlist(request, product_id):

    wishlist, created = add_wishlist_service(request.user, product_id)

    if created:
        messages.success(request, "Đã thêm vào danh sách yêu thích")
    else:
        messages.info(request, "Sản phẩm đã có trong danh sách yêu thích")

    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required
def remove_wishlist(request, product_id):

    remove_wishlist_service(request.user, product_id)

    messages.success(request, "Đã xóa khỏi danh sách yêu thích")

    return redirect('wishlist')


