from django.urls import path
from . import views

urlpatterns = [
	path('add_req_wash', views.AddRequestWashView.as_view(), name="add_req_wash"),
	path('add_req_stock', views.AddRequestStockView.as_view(), name="add_req_stock"),
	path('add_req_cons', views.AddRequestConsumptionView.as_view(), name="add_req_cons"),
	path('add_req_other_cons', views.AddRequestOtherConsumptionView.as_view(), name="add_req_other_cons"),
]


