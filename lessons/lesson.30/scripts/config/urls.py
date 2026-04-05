from __future__ import annotations

from django.contrib import admin
from django.urls import path

from botmanager.views import admin_metrics_view, export_leads_csv_view, export_orders_csv_view

urlpatterns = [
    path("admin/metrics/", admin_metrics_view, name="admin-metrics"),
    path("admin/reports/leads.csv", export_leads_csv_view, name="admin-leads-export"),
    path("admin/reports/orders.csv", export_orders_csv_view, name="admin-orders-export"),
    path("admin/", admin.site.urls),
]
