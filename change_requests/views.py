from django.views import View
from django.shortcuts import render, redirect
from telegram import Bot
from asgiref.sync import async_to_sync
from carwash.models import Wash
from warehouse.models import StockConsumption
from accounting.models import Consumption, OtherConsumption
from .models import RequestWash, RequestStock, RequestConsumption, RequestOtherConsumption


class BaseAddRequestView(View):
	"""
	Базовый класс для добавления запроса на изменение
	"""
	main_model = None
	form_class = None
	model_class = None
	template_name = None
	text = None
	chat_id = '680756851'
	chat_key = '6459249828:AAFXi42CTcMl1Un7Z5b2XuAOS9rc3sdcZGA'

	async def send_telegram_message(self, text):
		bot = Bot(token=self.chat_key)
		await bot.send_message(chat_id=self.chat_id, text=text)

	def post(self, request):
		from .forms import AddRequestWashForm, AddRequestStockForm, AddRequestConsumptionForm, AddRequestOtherConsumptionForm
		form_class = getattr(self, 'form_class', AddRequestWashForm)
		form = form_class(request.POST)

		if form.is_valid():
			obj_id = int(request.POST.get("rw-id"))
			description = form.cleaned_data.get("description")

			req = self.model_class.objects.create(
				**{"obj": self.main_model.objects.get(id=obj_id), "description": description}
			)
			model_name = str(self.main_model.__name__).lower()
			domain = request.build_absolute_uri('/')[:-1]
			message = f'**Запрос на изменение.** \n**Описание:**\n{description} \n**Ссылка:** \n{domain}/admin/{self.main_model._meta.app_label}/{model_name}/{obj_id}/change/'
			#self.send_telegram_message(')
			async_to_sync(self.send_telegram_message)(message)
			return redirect("menu")

		return render(request, self.template_name, {"req_wash_form": form})


class AddRequestWashView(BaseAddRequestView):
	"""
	Добавление запроса на изменение мойки
	"""
	main_model = Wash
	form_class = None  # будет установлен в post методе
	model_class = RequestWash
	template_name = "menu.html"


class AddRequestStockView(BaseAddRequestView):
	"""
	Добавление запроса на изменение склада
	"""
	main_model = StockConsumption
	form_class = None
	model_class = RequestStock
	template_name = "menu.html"


class AddRequestConsumptionView(BaseAddRequestView):
	"""
	Добавление запроса на изменение расхода
	"""
	main_model = Consumption
	form_class = None
	model_class = RequestConsumption
	template_name = "menu.html"


class AddRequestOtherConsumptionView(BaseAddRequestView):
	"""
	Добавление запроса на изменение бытового расхода
	"""
	main_model = OtherConsumption
	form_class = None
	model_class = RequestOtherConsumption
	template_name = "menu.html"