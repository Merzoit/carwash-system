from django.views.generic import TemplateView
from shared_algorythms import Math
from carwash.models import Shift, Service, Washman
from warehouse.models import Stock, StockConsumption
from accounting.models import Consumption, OtherConsumption
from change_requests.models import RequestWash, RequestStock, RequestConsumption, RequestOtherConsumption
from system_settings.forms import AddShiftForm, AddCarClassForm


class Dashboard(TemplateView):
	"""
	Панель администратора
	"""
	template_name = "dashboard.html"

	def __init__(self):
		self.shift = Shift.objects.last()
		self.math = Math()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["consumption"] = Consumption.objects.filter(shift=self.shift)
		context["consumption_sum"] = self.math.shift_washmans_consumption(self.shift)
		#БЫТ
		context["other_consumption"] = OtherConsumption.objects.filter(shift=self.shift)
		context["other_consumption_sum"] = self.math.shift_other_consumption(shift=self.shift)
		#СКЛАД
		context["stock_consumption"] = StockConsumption.objects.filter(shift=self.shift)
		context["stock_consumption_sum"] = self.math.shift_stock_consumption(self.shift)
		context["balance"] = self.math.shift_balance(self.shift)
		context["shift"] = self.shift
		context["shift_form"] = AddShiftForm
		context["drop_balance"] = self.math.shift_drop_balance(self.shift)
		context["full_balance"] = self.math.shift_balance(self.shift)["sale"] + self.math.shift_stock_consumption(self.shift)
		context["admin_consumption"] = self.math.shift_admin_consumption(self.shift)
		context["close_cash"] = self.math.shift_drop_balance(self.shift)["cash"] - self.math.shift_washmans_consumption(self.shift) - self.math.shift_other_consumption(shift=self.shift) - self.math.shift_admin_consumption(self.shift)

		#dashboard
		context["dash_shift_list"] = Shift.objects.all().order_by("-id")
		context["dash_service_list"] = Service.objects.all().order_by("-id")
		context["dash_staff_list"] = Washman.objects.all().order_by("-id")
		context["dash_stock_list"] = Stock.objects.all().order_by("-id")
		context["dash_add_car_class_form"] = AddCarClassForm
		context["dash_salary_report"] = Consumption.objects.all().order_by("-id")
		context["dash_stock_report"] = StockConsumption.objects.all().order_by("-id")
		context["dash_other_report"] = OtherConsumption.objects.all().order_by("-id")
		context["dash_wash_request"] = RequestWash.objects.filter(is_active=True).order_by("-id")
		context["dash_stock_request"] = RequestStock.objects.filter(is_active=True).order_by("-id")
		context["dash_consumption_request"] = RequestConsumption.objects.filter(is_active=True).order_by("-id")
		context["dash_other_consumption_request"] = RequestOtherConsumption.objects.filter(is_active=True).order_by("-id")
		return context