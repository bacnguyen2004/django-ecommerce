from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required


from ...services.web.wishlist import(
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
        'app/web/cart/wishlist.html',
        context
    )

@login_required
def add_wishlist(request, product_id):

    add_wishlist_service(request.user, product_id)

    return redirect('home')

@login_required
def remove_wishlist(request, product_id):

    remove_wishlist_service(request.user, product_id)

    return redirect('wishlist')