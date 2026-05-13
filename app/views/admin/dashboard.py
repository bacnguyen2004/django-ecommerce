from django.shortcuts import render

from app.decorators import admin_required

from app.services.admin.dashboard import (
    get_dashboard_data_service
)


@admin_required
def dashboard(request):

    context = get_dashboard_data_service()

    return render(
        request,
        "app/admin/dashboard/index.html",
        context
    )