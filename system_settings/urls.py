from django.urls import path
from . import views

urlpatterns = [
	path("add_shift", views.AddShiftView.as_view(), name="add_shift"),
]


