from django.urls import path
from . import views
from warehouse import views as warehouse_views

urlpatterns = [
    path("menu", views.Menu.as_view(), name="menu"),
    path("add", views.AddView.as_view(), name="add"),
    path("warehouse", warehouse_views.WarehouseView.as_view(), name="warehouse"),
    path("personnel", views.PersonnelView.as_view(), name="personnel"),
    path("payments", views.PaymentsView.as_view(), name="payments"),
    path("clients", views.ClientsView.as_view(), name="clients"),
    path('add_wash', views.WashAddView.as_view(), name="add_wash"),
    path('add_stock_cons', warehouse_views.AddStockView.as_view(), name="add_stock_cons"),
    path('add_washman', views.PersonnelView.as_view(), name="add_washman"),
    path('toggle_washman_status', views.PersonnelView.as_view(), name="toggle_washman_status"),
    path("settings", views.SettingsView.as_view(), name="settings"),
    path("analytics", views.AnalyticsView.as_view(), name="analytics"),
    path("help", views.HelpView.as_view(), name="help"),
    path("health/", views.HealthCheckView.as_view(), name="health_check"),
]
