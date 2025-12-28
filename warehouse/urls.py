from django.urls import path
from . import views

urlpatterns = [
	path("add_stock", views.AddStockView.as_view(), name="add_stock_cons"),
	path("inventory", views.InventoryView.as_view(), name="inventory"),
]


