from django.urls import path
from . import views

urlpatterns = [
    path("", views.Login.as_view(), name="login"),
    path("menu", views.Menu.as_view(), name="menu"),
    path("add", views.AddView.as_view(), name="add"),
	path('add_wash', views.WashAddView.as_view(), name="add_wash"),
	#path('add_wash_done', views.WashAddDone.as_view(), name="add_wash_done"),
	path('add_req_wash', views.AddRequestWashView.as_view(), name="add_req_wash"),
	path('add_req_stock', views.AddRequestStockView.as_view(), name="add_req_stock"),
	path('add_req_cons', views.AddRequestConsumptionView.as_view(), name="add_req_cons"),
	path('add_req_other_cons', views.AddRequestOtherConsumptionView.as_view(), name="add_req_other_cons"),
	path("add_cons", views.AddConsView.as_view(), name="add_cons"),
	path("add_other_cons", views.AddOtherConsView.as_view(), name="add_other_cons"),
	path("add_stock", views.AddStockView.as_view(), name="add_stock_cons"),
	path("add_shift", views.AddShiftView.as_view(), name="add_shift"),
	
	path("dashboard", views.Dashboard.as_view(), name="dashboard"),
	#path("dashboard/add_car_class", views.AddCarClass.as_view(), name="dash_add_car_class"),
	#path('dashboard/shift/delete/<int:obj_id>/', views.delete_shift, name='delete_shift'),
	#path('dashboard/service/delete/<int:obj_id>/', views.delete_service, name='delete_service'),
	#path('dashboard/washman/delete/<int:obj_id>/', views.delete_washman, name='delete_washman'),
]
