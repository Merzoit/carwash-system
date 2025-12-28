from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from telegram import Bot
from asgiref.sync import async_to_sync
# Create your views here.
from .forms import (
	LoginForm,  # Форма для обработки процесса аутентификации пользователей.
	AddWashForm,  # Форма для добавления информации о процессе стирки или аналогичной операции.
	AddConsForm,  # Форма для внесения данных о потреблении определенных ресурсов.
	AddOtherConsForm,  # Форма для записи других типов потребления ресурсов.
	AddShiftForm,  # Форма для добавления информации о сменах, включая время и данные сотрудников.
	AddRequestWashForm,  # Форма для запроса услуги стирки или аналогичной операции.
	AddRequestStockForm,  # Форма для запроса запасных частей или ресурсов, включая детали и количество.
	AddRequestConsumptionForm,  # Форма для запроса определенных потребительских товаров.
	AddRequestOtherConsumptionForm,  # Форма для запроса других типов потребительских товаров.
	AddCarClassForm,
)
from .models import *
from .algorythm import *


class Login(LoginView):
	"""
	Вход на сайт
	"""
	template_name = "login.html"
	form_class = LoginForm
	succes_url = reverse_lazy('login')
	
	def get_succes_url(self):
		return self.succes_url
		
		
class Menu(TemplateView, Math):
	"""
	Меню
	"""
	template_name = "stat.html"
	
	def __init__(self):
		self.shift = Shift.objects.last()
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["Wash"] = Wash.objects.filter(shift=self.shift).order_by("-id")
		context["washman"] = Washman.objects.all()
		context["stock"] = Stock.objects.all()
		context["shift"] = self.shift
		#ФОРМЫ
		context["form"] = AddWashForm
		context["c_form"] = AddConsForm
		context["oc_form"] = AddOtherConsForm
		context["shift_form"] = AddShiftForm
		context["req_wash_form"] = AddRequestWashForm
		context["req_stock_form"] = AddRequestStockForm
		context["req_cons_form"] = AddRequestConsumptionForm
		context["req_other_cons_form"] = AddRequestOtherConsumptionForm
		#ЗАРПЛАТА МОЙЩИКОВ
		context["consumption"] = Consumption.objects.filter(shift=self.shift)
		context["consumption_sum"] = self.shift_washmans_consumption(self.shift)
		#БЫТ
		context["other_consumption"] = OtherConsumption.objects.filter(shift=self.shift)
		context["other_consumption_sum"] = self.shift_other_consumption(shift=self.shift)
		#СКЛАД
		context["stock_consumption"] = StockConsumption.objects.filter(shift=self.shift)
		context["stock_consumption_sum"] = self.shift_stock_consumption(self.shift)
		#СТАТИСТИКА МОЙКИ
		context["balance"] = self.shift_balance(self.shift)
		context["drop_balance"] = self.shift_drop_balance(self.shift)
		context["full_balance"] = self.shift_balance(self.shift)["sale"] + self.shift_stock_consumption(self.shift)
		context["admin_consumption"] = self.shift_admin_consumption(self.shift)
		context["close_cash"] = self.shift_drop_balance(self.shift)["cash"] - self.shift_washmans_consumption(self.shift) - self.shift_other_consumption(shift=self.shift) - self.shift_admin_consumption(self.shift)
		return context
		

class AddView(TemplateView, Math):
	template_name = "add.html"
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["form"] = AddWashForm
		return context
		
class WashAddView(View, Management, Math):
	"""
	Добавление мойки
	"""
	def post(self, request):
		shift = Shift.objects.last()
		car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, price = self.extract_data(request)
		services = self.get_selected_services(request)

		services_price = self.calculate_services_price(services, car_class)
		services_price = self.apply_sale(services_price, sale)
		services_price = self.apply_add(services_price, add)
		services_price = self.apply_night_discount(services_price, night, dry, polishing)
		
		washman_money = 0
		settings = self.get_settings()
		
		if dry:
			washman_money = services_price * settings.washman_dry_percent
		elif polishing:
			washman_money = services_price * settings.washman_poly_percent
		else:
			washman_money = services_price * (settings.washman_night_percent if night else settings.washman_percent)
		
		data = {
            'grz': grz,
            'mark': mark,
            'car_class': car_class,
            'washman': Washman.objects.get(id=washman).name,
            'pay': Pay.objects.get(id=pay).name,
            'dry': dry,
            'polishing': polishing,
            'night': night,
            'service': services, 
            'sale': sale,
            'add': add,
            'price': services_price,
            'washman_money': washman_money,
        }
        
		if 'preview_wash' in request.POST:
			return render(request, 'wash_demo.html', data)
		elif 'add_wash' in request.POST:
			wash = self.create_wash_object(shift.id, car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, services_price, services, washman_money)
			obj = Washman.objects.get(id=washman)
			obj.balance += washman_money
			obj.save()
			messages.success(request, 'Мойка успешно добавлена!')
			return redirect('menu')

		return render(request, 'wash_demo.html', data)


class AddConsView(View):
	"""
	Добавление выплаты
	"""
	def post(self, request):
		shift = Shift.objects.last()
		washman = request.POST.get("washman")
		money = request.POST.get("money")
		
		cons = Consumption.objects.create(
			shift=shift,
			washman=Washman.objects.get(id=washman),
			money=money,
			)
		man = Washman.objects.get(id=washman)
		man.balance -= int(money)
		man.save()
		return redirect(f"menu")
		
		
class AddOtherConsView(View):
	"""
	Добавление бытового расхода
	"""
	def post(self, request):
		shift = Shift.objects.last()
		description = request.POST.get("description")
		money = request.POST.get("money")
		
		other_cons = OtherConsumption.objects.create(
			shift=shift,
			description=description,
			money=money,
			)

		return redirect(f'menu')
		
		
class AddStockView(View):
	"""
	Добавление склада
	"""
	def post(self, request):
		shift = Shift.objects.last()
		stock = request.POST.get("stock")
		stock_price = Stock.objects.get(id=stock).price
		quantity = request.POST.get("quant")
		pay = request.POST.get("pay")
		price = int(quantity) * int(stock_price)
		
		data = {
			'stock': Stock.objects.get(id=stock).name,
			'stock_price': stock_price,
			'quantity': quantity,
			'pay': Pay.objects.get(id=pay).name,
			'price': price,
		}
		
		if 'preview_stock' in request.POST:
			return render(request, 'stock_demo.html', data)
		elif 'add_stock' in request.POST:
			stock_cons = StockConsumption.objects.create(
				shift=shift,
				stock=Stock.objects.get(id=stock),
				quantity=quantity,
				pay=Pay.objects.get(id=pay),
				money=price,
				)
				
			stock_obj = Stock.objects.get(id=stock)
			stock_obj.quantity -= int(quantity)
			stock_obj.save()
			return redirect(f'menu')
			
		return render(request, 'stock_demo.html', data)

class AddShiftView(View):
	"""
	Открытие смены
	"""
	def post(self, request):
		shift_form = AddShiftForm(request.POST)
		if shift_form.is_valid():
			shift_form.save()
			return redirect('menu')

		return render(request, 'menu.html', {'shift_form': shift_form})


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
		form = self.form_class(request.POST)
		
		if form.is_valid():
			obj_id = int(request.POST.get("rw-id"))
			description = form.cleaned_data.get("description")
			
			req = self.model_class.objects.create(
				**{"obj": self.main_model.objects.get(id=obj_id), "description": description}
			)
			model_name = str(self.main_model.__name__).lower()
			domain = request.build_absolute_uri('/')[:-1]
			message = f'**Запрос на изменение.** \n**Описание:**\n{description} \n**Ссылка:** \n{domain}/admin/core/{model_name}/{obj_id}/change/'
			#self.send_telegram_message(')
			async_to_sync(self.send_telegram_message)(message)
			return redirect("menu")
			
		return render(request, self.template_name, {"req_wash_form": form})


class AddRequestWashView(BaseAddRequestView):
	"""
	Добавление запроса на изменение мойки
	"""
	main_model = Wash
	form_class = AddRequestWashForm
	model_class = RequestWash
	template_name = "menu.html"


class AddRequestStockView(BaseAddRequestView):
	"""
	Добавление запроса на изменение склада
	"""
	main_model = StockConsumption
	form_class = AddRequestStockForm
	model_class = RequestStock
	template_name = "menu.html"
	

class AddRequestConsumptionView(BaseAddRequestView):
	"""
	Добавление запроса на изменение мойки
	"""
	main_model = Consumption
	form_class = AddRequestConsumptionForm
	model_class = RequestConsumption
	template_name = "menu.html"


class AddRequestOtherConsumptionView(BaseAddRequestView):
	"""
	Добавление запроса на изменение склада
	"""
	main_model = OtherConsumption
	form_class = AddRequestOtherConsumptionForm
	model_class = RequestOtherConsumption
	template_name = "menu.html"
	
	
class Dashboard(TemplateView, Math):
	"""
	Панель администратора
	"""
	template_name = "dashboard.html"
	
	def __init__(self):
		self.shift = Shift.objects.last()
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["consumption"] = Consumption.objects.filter(shift=self.shift)
		context["consumption_sum"] = self.shift_washmans_consumption(self.shift)
		#БЫТ
		context["other_consumption"] = OtherConsumption.objects.filter(shift=self.shift)
		context["other_consumption_sum"] = self.shift_other_consumption(shift=self.shift)
		#СКЛАД
		context["stock_consumption"] = StockConsumption.objects.filter(shift=self.shift)
		context["stock_consumption_sum"] = self.shift_stock_consumption(self.shift)
		context["balance"] = self.shift_balance(self.shift)
		context["shift"] = self.shift
		context["shift_form"] = AddShiftForm
		context["drop_balance"] = self.shift_drop_balance(self.shift)
		context["full_balance"] = self.shift_balance(self.shift)["sale"] + self.shift_stock_consumption(self.shift)
		context["admin_consumption"] = self.shift_admin_consumption(self.shift)
		context["close_cash"] = self.shift_drop_balance(self.shift)["cash"] - self.shift_washmans_consumption(self.shift) - self.shift_other_consumption(shift=self.shift) - self.shift_admin_consumption(self.shift)
		
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
		
		

		