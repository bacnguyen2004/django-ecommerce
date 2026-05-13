from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated:

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            customer = getattr(request.user, 'customer', None)

            if customer and customer.role == 'admin':
                return view_func(request, *args, **kwargs)

        return redirect('home')

    return wrapper