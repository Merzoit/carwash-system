from django.urls import path
from . import views

urlpatterns = [
	path("add_cons", views.AddConsView.as_view(), name="add_cons"),
	path("add_other_cons", views.AddOtherConsView.as_view(), name="add_other_cons"),
]


