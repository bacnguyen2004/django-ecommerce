from django.shortcuts import redirect

def admin_required(view_func):

    def wrapper(request, *args, **kwargs):

        if request.user.is_authenticated:

            if request.user.customer.role == 'admin':

                return view_func(
                    request,
                    *args,
                    **kwargs
                )

        return redirect('home')

    return wrapper