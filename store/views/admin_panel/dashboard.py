from django.shortcuts import render

from store.decorators import admin_required

from store.services.admin_panel.dashboard import (
    get_dashboard_data_service
)


@admin_required
def dashboard(request):

    context = get_dashboard_data_service()

    return render(
        request,
        "store/admin_panel/dashboard/index.html",
        context
    )

