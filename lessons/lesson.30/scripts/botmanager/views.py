from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse

from .services import (
    build_leads_csv,
    build_orders_csv,
    get_metrics_for_display,
    get_active_prompt_name,
)


@staff_member_required
def admin_metrics_view(request: HttpRequest) -> HttpResponse:
    context = {
        **admin.site.each_context(request),
        "title": "Метрики бота заказов курсов",
        "metrics": get_metrics_for_display(),
        "active_prompt_name": get_active_prompt_name(),
    }
    return TemplateResponse(request, "botmanager/metrics.html", context)


@staff_member_required
def export_leads_csv_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(build_leads_csv(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="leads-report.csv"'
    return response


@staff_member_required
def export_orders_csv_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(build_orders_csv(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="orders-report.csv"'
    return response
