from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from shared_algorythms import Management, Math
from .models import *
from warehouse.models import Stock


class Menu(TemplateView):
	"""
	Меню
	"""
	template_name = "stat.html"

	def __init__(self):
		self.shift = Shift.objects.last()
		self.math = Math()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["Wash"] = Wash.objects.filter(shift=self.shift).order_by("-id")
		context["washman"] = Washman.objects.all()
		context["stock"] = Stock.objects.all()
		context["shift"] = self.shift
		#ФОРМЫ
		from .forms import AddWashForm
		from accounting.forms import AddConsForm, AddOtherConsForm
		from system_settings.forms import AddShiftForm
		from change_requests.forms import AddRequestWashForm, AddRequestStockForm, AddRequestConsumptionForm, AddRequestOtherConsumptionForm
		context["form"] = AddWashForm
		context["c_form"] = AddConsForm
		context["oc_form"] = AddOtherConsForm
		context["shift_form"] = AddShiftForm
		context["req_wash_form"] = AddRequestWashForm
		context["req_stock_form"] = AddRequestStockForm
		context["req_cons_form"] = AddRequestConsumptionForm
		context["req_other_cons_form"] = AddRequestOtherConsumptionForm
		#ЗАРПЛАТА МОЙЩИКОВ
		from accounting.models import Consumption
		context["consumption"] = Consumption.objects.filter(shift=self.shift)
		context["consumption_sum"] = self.math.shift_washmans_consumption(self.shift)
		#БЫТ
		from accounting.models import OtherConsumption
		context["other_consumption"] = OtherConsumption.objects.filter(shift=self.shift)
		context["other_consumption_sum"] = self.math.shift_other_consumption(shift=self.shift)
		#СКЛАД
		from warehouse.models import StockConsumption
		context["stock_consumption"] = StockConsumption.objects.filter(shift=self.shift)
		context["stock_consumption_sum"] = self.math.shift_stock_consumption(self.shift)
		#СТАТИСТИКА МОЙКИ
		context["balance"] = self.math.shift_balance(self.shift)
		context["drop_balance"] = self.math.shift_drop_balance(self.shift)
		context["full_balance"] = self.math.shift_balance(self.shift)["sale"] + self.math.shift_stock_consumption(self.shift)
		context["admin_consumption"] = self.math.shift_admin_consumption(self.shift)
		# Рассчитываем остаток наличных - ищем тип оплаты содержащий "наличн"
		drop_balance = self.math.shift_drop_balance(self.shift)
		cash_amount = 0
		for pay_type, amount in drop_balance.items():
			if 'наличн' in pay_type.lower():
				cash_amount = amount
				break

		context["close_cash"] = cash_amount - self.math.shift_washmans_consumption(self.shift) - self.math.shift_other_consumption(shift=self.shift) - self.math.shift_admin_consumption(self.shift)
		return context


class AddView(TemplateView):
	template_name = "add.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		from .forms import AddWashForm
		from .models import Wash, Shift, Client

		context["form"] = AddWashForm

		# Получаем список клиентов для автодополнения
		clients = Client.objects.all().order_by('license_plate')
		context["clients"] = list(clients.values('id', 'license_plate', 'name', 'discount'))

		# Получаем мойки текущей смены
		try:
			current_shift = Shift.objects.last()
			if current_shift:
				washes = Wash.objects.filter(shift=current_shift).order_by('-time')
				context["current_shift_washes"] = washes
				context["total_washes"] = washes.count()
				context["total_revenue"] = sum(wash.price for wash in washes)
			else:
				context["current_shift_washes"] = []
				context["total_washes"] = 0
				context["total_revenue"] = 0
		except:
			context["current_shift_washes"] = []
			context["total_washes"] = 0
			context["total_revenue"] = 0

		return context


class WarehouseView(TemplateView):
	template_name = "warehouse.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		from warehouse.forms import StockConsumptionForm
		from warehouse.models import StockConsumption, Stock
		from carwash.models import Shift

		context["stock_form"] = StockConsumptionForm

		# Получаем складские операции текущей смены
		try:
			current_shift = Shift.objects.last()
			if current_shift:
				stock_operations = StockConsumption.objects.filter(shift=current_shift).order_by('-id')
				context["current_shift_stock_operations"] = stock_operations
				context["total_operations"] = stock_operations.count()
				context["total_consumption"] = sum(op.money for op in stock_operations)
			else:
				context["current_shift_stock_operations"] = []
				context["total_operations"] = 0
				context["total_consumption"] = 0
		except:
			context["current_shift_stock_operations"] = []
			context["total_operations"] = 0
			context["total_consumption"] = 0

		return context


class PaymentsView(View):
	"""
	Управление выплатами мойщикам и расходниками
	"""
	template_name = "payments.html"

	def get(self, request):
		from accounting.forms import AddConsForm, AddOtherConsForm
		from accounting.models import Consumption, OtherConsumption
		from .models import Washman, Wash
		from django.db.models import Sum

		context = {
			"consumption_form": AddConsForm,
			"other_consumption_form": AddOtherConsForm
		}

		# Получаем текущую смену
		try:
			current_shift = Shift.objects.last()
			context["current_shift"] = current_shift
		except:
			current_shift = None
			context["current_shift"] = None

		if current_shift:
			# Получаем всех активных сотрудников
			active_washmen = Washman.objects.filter(is_active=True).order_by('name')

			# Рассчитываем статистику для каждого сотрудника
			washmen_payments = []
			total_earned = 0
			total_paid = 0

			for washman in active_washmen:
				# Заработок за текущую смену
				shift_earnings = Wash.objects.filter(
					washman=washman,
					shift=current_shift
				).aggregate(total=Sum('washman_money'))['total'] or 0

				# Уже выплаченные суммы за текущую смену
				shift_payments = Consumption.objects.filter(
					washman=washman,
					shift=current_shift
				).aggregate(total=Sum('money'))['total'] or 0

				# Остаток к выплате
				remaining = shift_earnings - shift_payments

				# Процент выплат для прогресс-бара
				payment_percentage = 0
				if shift_earnings > 0:
					payment_percentage = int((shift_payments / shift_earnings) * 100)

				washmen_payments.append({
					'washman': washman,
					'shift_earnings': shift_earnings,
					'shift_payments': shift_payments,
					'remaining': remaining,
					'balance': washman.balance,
					'payment_percentage': payment_percentage,
				})

				total_earned += shift_earnings
				total_paid += shift_payments

			context["washmen_payments"] = washmen_payments
			context["total_earned"] = total_earned
			context["total_paid"] = total_paid
			context["total_remaining"] = total_earned - total_paid

			# Рассчитываем прогресс для круговой диаграммы
			if total_earned > 0:
				context["progress_percentage"] = int((total_paid / total_earned) * 100)
				context["progress_stroke"] = 219.91 * (total_paid / total_earned)
			else:
				context["progress_percentage"] = 0
				context["progress_stroke"] = 0

			# Получаем последние выплаты за текущую смену
			recent_payments = Consumption.objects.filter(
				shift=current_shift
			).order_by('-id')[:10]  # Последние 10 выплат
			context["recent_payments"] = recent_payments

			# Получаем расходники за текущую смену
			other_consumptions = OtherConsumption.objects.filter(
				shift=current_shift
			).order_by('-id')
			context["other_consumptions"] = other_consumptions
			context["total_other_consumption"] = sum(oc.money for oc in other_consumptions)

			# Статистика по категориям расходников
			other_consumption_stats = {}
			for oc in other_consumptions:
				category = oc.description.lower()
				if category not in other_consumption_stats:
					other_consumption_stats[category] = {
						'description': oc.description,
						'total': 0,
						'count': 0
					}
				other_consumption_stats[category]['total'] += oc.money
				other_consumption_stats[category]['count'] += 1

			context["other_consumption_stats"] = list(other_consumption_stats.values())

		else:
			context["washmen_payments"] = []
			context["total_earned"] = 0
			context["total_paid"] = 0
			context["total_remaining"] = 0
			context["recent_payments"] = []
			context["other_consumptions"] = []
			context["total_other_consumption"] = 0
			context["other_consumption_stats"] = []

		return render(request, self.template_name, context)

	def post(self, request):
		from accounting.forms import AddConsForm, AddOtherConsForm
		from accounting.models import Consumption, OtherConsumption
		from django.contrib import messages

		if 'add_payment' in request.POST:
			form = AddConsForm(request.POST)
			if form.is_valid():
				try:
					current_shift = Shift.objects.last()
					consumption = form.save(commit=False)
					consumption.shift = current_shift
					consumption.save()

					# Обновляем баланс мойщика
					washman = consumption.washman
					washman.balance -= consumption.money
					washman.save()

					messages.success(request, f'Выплата {consumption.money} ₽ сотруднику "{washman.name}" успешно добавлена!')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении выплаты: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме. Проверьте введенные данные.')

		elif 'add_other_consumption' in request.POST:
			form = AddOtherConsForm(request.POST)
			if form.is_valid():
				try:
					current_shift = Shift.objects.last()
					other_consumption = form.save(commit=False)
					other_consumption.shift = current_shift
					other_consumption.save()

					messages.success(request, f'Расход "{other_consumption.description}" на сумму {other_consumption.money} ₽ успешно добавлен!')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении расхода: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме расхода. Проверьте введенные данные.')

		return redirect('payments')


class ClientsView(View):
	"""
	Управление клиентами автомойки
	"""
	template_name = "clients.html"

	def get(self, request):
		from .forms import ClientForm
		from .models import Client, Wash
		from django.db.models import Count, Sum

		context = {
			"client_form": ClientForm
		}

		# Получаем всех клиентов
		clients = Client.objects.all().order_by('name')
		context["clients"] = clients
		context["total_clients"] = clients.count()

		# Статистика по клиентам
		clients_stats = []
		for client in clients:
			# Количество посещений (моек)
			total_visits = Wash.objects.filter(grz__iexact=client.license_plate).count()
			# Общая сумма оплат
			total_spent = Wash.objects.filter(grz__iexact=client.license_plate).aggregate(
				total=Sum('price')
			)['total'] or 0

			clients_stats.append({
				'client': client,
				'total_visits': total_visits,
				'total_spent': total_spent,
				'average_bill': total_spent / total_visits if total_visits > 0 else 0,
			})

		context["clients_stats"] = clients_stats

		return render(request, self.template_name, context)

	def post(self, request):
		from .forms import ClientForm
		from .models import Client
		from django.contrib import messages

		if 'add_client' in request.POST:
			form = ClientForm(request.POST)
			if form.is_valid():
				try:
					client = form.save()
					messages.success(request, f'Клиент "{client.name}" успешно добавлен!')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении клиента: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме. Проверьте введенные данные.')

		return redirect('clients')


class SettingsView(View):
	"""
	Управление настройками автомойки
	"""
	template_name = "settings.html"

	def get(self, request):
		from .forms import CarClassForm, PayForm, ServiceForm, WashPriceListForm
		from .models import CarClass, Pay, Service, WashPriceList
		from system_settings.forms import SystemSettingsForm
		from system_settings.models import Settings

		context = {
			"car_class_form": CarClassForm,
			"pay_form": PayForm,
			"service_form": ServiceForm,
			"price_list_form": WashPriceListForm,
			"system_settings_form": SystemSettingsForm,
		}

		# Получаем все данные для отображения
		context["car_classes"] = CarClass.objects.all().order_by('name')
		context["pay_types"] = Pay.objects.all().order_by('name')
		context["services"] = Service.objects.all().order_by('name')
		context["price_list"] = WashPriceList.objects.all().select_related('service', 'car_class').order_by('service__name', 'car_class__name')

		# Статистика
		context["total_car_classes"] = context["car_classes"].count()
		context["total_pay_types"] = context["pay_types"].count()
		context["total_services"] = context["services"].count()
		context["total_price_entries"] = context["price_list"].count()

		# Системные настройки
		context["system_settings"] = Settings.objects.all().order_by('-is_active', '-id')

		return render(request, self.template_name, context)

	def post(self, request):
		from .forms import CarClassForm, PayForm, ServiceForm, WashPriceListForm
		from .models import CarClass, Pay, Service, WashPriceList
		from django.contrib import messages

		if 'add_car_class' in request.POST:
			form = CarClassForm(request.POST)
			if form.is_valid():
				try:
					car_class = form.save()
					messages.success(request, f'Класс ТС "{car_class.name}" успешно добавлен!')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении класса ТС: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме класса ТС. Проверьте введенные данные.')

		elif 'add_pay_type' in request.POST:
			form = PayForm(request.POST)
			if form.is_valid():
				try:
					pay_type = form.save()
					messages.success(request, f'Тип оплаты "{pay_type.name}" успешно добавлен!')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении типа оплаты: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме типа оплаты. Проверьте введенные данные.')

		elif 'add_service' in request.POST:
			form = ServiceForm(request.POST)
			if form.is_valid():
				try:
					service = form.save()
					messages.success(request, f'Услуга "{service.name}" успешно добавлена!')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении услуги: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме услуги. Проверьте введенные данные.')

		elif 'add_price_entry' in request.POST:
			form = WashPriceListForm(request.POST)
			if form.is_valid():
				try:
					# Проверяем, существует ли уже такая запись
					service = form.cleaned_data['service']
					car_class = form.cleaned_data['car_class']

					existing_entry = WashPriceList.objects.filter(
						service=service,
						car_class=car_class
					).first()

					if existing_entry:
						# Обновляем существующую запись
						existing_entry.price = form.cleaned_data['price']
						existing_entry.save()
						messages.success(request, f'Цена для услуги "{service.name}" и класса "{car_class.name}" успешно обновлена!')
					else:
						# Создаем новую запись
						price_entry = form.save()
						messages.success(request, f'Цена для услуги "{service.name}" и класса "{car_class.name}" успешно добавлена!')
				except Exception as e:
					messages.error(request, f'Ошибка при сохранении цены: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме прайс-листа. Проверьте введенные данные.')

		elif 'add_system_settings' in request.POST:
			from system_settings.forms import SystemSettingsForm
			from system_settings.models import Settings
			form = SystemSettingsForm(request.POST)
			if form.is_valid():
				try:
					settings = form.save()
					status = "активна" if settings.is_active else "неактивна"
					messages.success(request, f'Системная настройка "{settings.name}" успешно {"активирована" if settings.is_active else "создана"}! Статус: {status}')
				except Exception as e:
					messages.error(request, f'Ошибка при сохранении настроек: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме системных настроек. Проверьте введенные данные.')

		elif 'activate_setting' in request.POST:
			from system_settings.models import Settings
			setting_id = request.POST.get('activate_setting')
			try:
				setting = Settings.objects.get(id=setting_id)
				# Деактивируем все остальные настройки
				Settings.objects.filter(is_active=True).update(is_active=False)
				# Активируем выбранную настройку
				setting.is_active = True
				setting.save()
				messages.success(request, f'Настройка "{setting.name}" успешно активирована!')
			except Settings.DoesNotExist:
				messages.error(request, 'Настройка не найдена.')
			except Exception as e:
				messages.error(request, f'Ошибка при активации настройки: {str(e)}')

		elif 'update_system_settings' in request.POST:
			from system_settings.forms import SystemSettingsForm
			from system_settings.models import Settings
			setting_id = request.POST.get('setting_id')
			try:
				setting = Settings.objects.get(id=setting_id)
				form = SystemSettingsForm(request.POST, instance=setting)
				if form.is_valid():
					updated_setting = form.save()
					status = "активна" if updated_setting.is_active else "неактивна"
					messages.success(request, f'Настройка "{updated_setting.name}" успешно обновлена! Статус: {status}')
				else:
					messages.error(request, 'Ошибка в форме обновления настроек. Проверьте введенные данные.')
			except Settings.DoesNotExist:
				messages.error(request, 'Настройка не найдена.')
			except Exception as e:
				messages.error(request, f'Ошибка при обновлении настройки: {str(e)}')

		return redirect('settings')


class HelpView(View):
	"""
	Страница помощи и инструкций для администратора
	"""
	template_name = "help.html"

	def get(self, request):
		context = {}
		return render(request, self.template_name, context)


class AnalyticsView(View):
	"""
	Аналитика и дашборд автомойки
	"""
	template_name = "analytics.html"

	def get(self, request):
		from django.db.models import Sum, Count, Avg, Q, F
		from django.utils import timezone
		from datetime import timedelta
		from collections import defaultdict

		context = {}

		# Получаем текущую смену
		current_shift = Shift.objects.last()
		context['current_shift'] = current_shift

		if current_shift:
			# === СТАТИСТИКА ТЕКУЩЕЙ СМЕНЫ ===
			shift_washes = Wash.objects.filter(shift=current_shift)
			context['shift_wash_count'] = shift_washes.count()
			context['shift_total_revenue'] = shift_washes.aggregate(total=Sum('price'))['total'] or 0

			# Популярные услуги текущей смены
			shift_services = defaultdict(int)
			for wash in shift_washes:
				services = wash.service.all()  # Получаем связанные объекты услуг
				for service in services:
					shift_services[service.name] += 1

			context['shift_popular_services'] = sorted(shift_services.items(), key=lambda x: x[1], reverse=True)[:5]

			# Доходы по классам ТС текущей смены
			shift_car_classes = shift_washes.values('car_class__name').annotate(
				total_revenue=Sum('price'),
				wash_count=Count('id')
			).order_by('-total_revenue')

			context['shift_car_classes'] = list(shift_car_classes)

			# === ОБЩАЯ СТАТИСТИКА ===
			all_washes = Wash.objects.all()

			# Общая статистика
			total_washes = all_washes.count()
			total_revenue = all_washes.aggregate(total=Sum('price'))['total'] or 0
			avg_wash_price = all_washes.aggregate(avg=Avg('price'))['avg'] or 0

			context.update({
				'total_washes': total_washes,
				'total_revenue': total_revenue,
				'avg_wash_price': round(avg_wash_price, 2),
			})

			# Статистика за последние 30 дней
			thirty_days_ago = timezone.now() - timedelta(days=30)
			recent_washes = all_washes.filter(time__gte=thirty_days_ago)

			context.update({
				'month_wash_count': recent_washes.count(),
				'month_revenue': recent_washes.aggregate(total=Sum('price'))['total'] or 0,
			})

			# Популярные услуги за все время
			all_services = defaultdict(int)
			for wash in all_washes:
				services = wash.service.all()  # Получаем связанные объекты услуг
				for service in services:
					all_services[service.name] += 1

			popular_services_list = sorted(all_services.items(), key=lambda x: x[1], reverse=True)[:10]
			# Добавляем процент для каждой услуги
			max_count = popular_services_list[0][1] if popular_services_list else 1
			popular_services_with_percent = []
			for service, count in popular_services_list:
				percentage = (count / max_count) * 100 if max_count > 0 else 0
				popular_services_with_percent.append((service, count, percentage))

			context['popular_services'] = popular_services_with_percent

			# Доходы по дням (последние 7 дней)
			seven_days_ago = timezone.now().date() - timedelta(days=7)
			daily_revenue = all_washes.filter(shift__date__gte=seven_days_ago).values(
				'shift__date'
			).annotate(
				day=F('shift__date'),
				revenue=Sum('price'),
				wash_count=Count('id')
			).order_by('shift__date')

			context['daily_revenue'] = list(daily_revenue)

			# Доходы по классам ТС за все время
			car_classes_stats = all_washes.values('car_class__name').annotate(
				total_revenue=Sum('price'),
				wash_count=Count('id'),
				avg_price=Avg('price')
			).order_by('-total_revenue')

			context['car_classes_stats'] = list(car_classes_stats)

			# Статистика по сотрудникам
			washmen_stats = Washman.objects.filter(is_active=True).annotate(
				total_washes=Count('wash'),
				total_revenue=Sum('wash__price'),
				avg_wash_price=Avg('wash__price')
			).order_by('-total_revenue')

			context['washmen_stats'] = list(washmen_stats)

			# Статистика по типам оплаты
			pay_types_list = all_washes.values('pay__name').annotate(
				total_revenue=Sum('price'),
				wash_count=Count('id')
			).order_by('-total_revenue')

			# Добавляем процент для каждого типа оплаты
			pay_types_with_percent = list(pay_types_list)
			max_revenue = pay_types_with_percent[0]['total_revenue'] if pay_types_with_percent else 1
			for pay_type in pay_types_with_percent:
				pay_type['percentage'] = (pay_type['total_revenue'] / max_revenue) * 100 if max_revenue > 0 else 0

			context['pay_types_stats'] = pay_types_with_percent

			# === ДАННЫЕ ДЛЯ ГРАФИКОВ ===
			# Данные для круговой диаграммы услуг
			services_chart_data = []
			for service, count, percentage in context['popular_services'][:5]:
				services_chart_data.append({
					'name': service,
					'value': count,
					'percentage': round((count / total_washes) * 100, 1) if total_washes > 0 else 0
				})
			context['services_chart_data'] = services_chart_data

			# Данные для линейного графика доходов
			revenue_chart_data = []
			for day_data in context['daily_revenue']:
				revenue_chart_data.append({
					'date': day_data['day'].strftime('%d.%m') if day_data['day'] else '',
					'revenue': float(day_data['revenue'] or 0),
					'washes': day_data['wash_count']
				})
			context['revenue_chart_data'] = revenue_chart_data

			# Данные для столбчатой диаграммы классов ТС
			car_classes_chart_data = []
			for car_class in context['car_classes_stats'][:6]:
				car_classes_chart_data.append({
					'name': car_class['car_class__name'] or 'Не указан',
					'revenue': float(car_class['total_revenue'] or 0),
					'washes': car_class['wash_count']
				})
			context['car_classes_chart_data'] = car_classes_chart_data

		return render(request, self.template_name, context)


class PersonnelView(View):
	"""
	Управление персоналом (мойщиками)
	"""
	template_name = "personnel.html"

	def get(self, request):
		from .forms import WashmanForm
		from .models import Washman, Wash
		from django.db.models import Count, Sum

		context = {
			"washman_form": WashmanForm
		}

		# Получаем всех сотрудников
		washmen = Washman.objects.all().order_by('name')
		context["washmen"] = washmen
		context["total_washmen"] = washmen.count()
		context["active_washmen"] = washmen.filter(is_active=True).count()
		context["inactive_washmen"] = washmen.filter(is_active=False).count()

		# Статистика по сотрудникам
		washmen_stats = []
		for washman in washmen:
			# Количество моек за все время
			total_washes = Wash.objects.filter(washman=washman).count()
			# Сумма заработка за все время
			total_earnings = Wash.objects.filter(washman=washman).aggregate(
				total=Sum('washman_money')
			)['total'] or 0

			# Мойки за текущую смену
			try:
				current_shift = Shift.objects.last()
				current_shift_washes = Wash.objects.filter(
					washman=washman, shift=current_shift
				).count()
			except:
				current_shift_washes = 0

			washmen_stats.append({
				'washman': washman,
				'total_washes': total_washes,
				'total_earnings': total_earnings,
				'current_shift_washes': current_shift_washes,
			})

		context["washmen_stats"] = washmen_stats

		return render(request, self.template_name, context)

	def post(self, request):
		from .forms import WashmanForm
		from .models import Washman
		from django.contrib import messages

		if 'add_washman' in request.POST:
			form = WashmanForm(request.POST)
			if form.is_valid():
				washman = form.save()
				messages.success(request, f'Сотрудник "{washman.name}" успешно добавлен!')
				return redirect('personnel')
			else:
				messages.error(request, 'Ошибка при добавлении сотрудника. Проверьте введенные данные.')

		elif 'toggle_status' in request.POST:
			washman_id = request.POST.get('washman_id')
			try:
				washman = Washman.objects.get(id=washman_id)
				washman.is_active = not washman.is_active
				washman.save()
				status = "активирован" if washman.is_active else "деактивирован"
				messages.success(request, f'Сотрудник "{washman.name}" {status}!')
			except Washman.DoesNotExist:
				messages.error(request, 'Сотрудник не найден.')

		return redirect('personnel')


class StockAddView(View, Management, Math):
	"""
	Добавление складской операции
	"""
	def post(self, request):
		from warehouse.models import Stock, StockConsumption
		from django.shortcuts import redirect
		from django.contrib import messages

		stock_id = request.POST.get('stock')
		quantity = int(request.POST.get('quantity', 0))
		pay_id = request.POST.get('pay')

		# Получаем объекты
		stock = Stock.objects.get(id=stock_id)
		pay = Pay.objects.get(id=pay_id)
		shift = Shift.objects.last()

		# Рассчитываем стоимость
		money = stock.price * quantity

		data = {
			'stock': stock.name,
			'stock_id': stock_id,
			'quantity': quantity,
			'pay': pay.name,
			'pay_id': pay_id,
			'money': money,
			'unit_price': stock.price,
		}

		if 'preview_stock' in request.POST:
			return render(request, 'stock_demo.html', data)
		elif 'add_stock' in request.POST:
			# Создаем запись о складской операции
			StockConsumption.objects.create(
				shift=shift,
				stock=stock,
				quantity=quantity,
				money=money,
				pay=pay
			)

			# Уменьшаем количество товара на складе
			stock.quantity -= quantity
			stock.save()

			messages.success(request, f'Складская операция успешно добавлена! Потрачено: {money} ₽')
			return redirect('warehouse')

		return render(request, 'stock_demo.html', data)


class WashAddView(View, Management, Math):
	"""
	Добавление мойки
	"""
	def post(self, request):
		from .models import Client

		shift = Shift.objects.last()
		car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, price = self.extract_data(request)
		services = self.get_selected_services(request)

		# Автоматическое определение скидки по гос номеру
		client_discount = 0
		client_name = None
		if grz:
			try:
				client = Client.objects.filter(license_plate__iexact=grz.strip()).first()
				if client:
					client_discount = client.discount
					client_name = client.name
			except:
				pass

		# Используем автоматическую скидку клиента, если ручная скидка не указана
		if not sale or sale == 0:
			sale = client_discount

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
            'car_class_id': car_class,
            'washman': Washman.objects.get(id=washman).name,
            'washman_id': washman,
            'pay': Pay.objects.get(id=pay).name,
            'pay_id': pay,
            'dry': dry,
            'polishing': polishing,
            'night': night,
            'service': services,
            'sale': sale,
            'add': add,
            'price': services_price,
            'washman_money': washman_money,
            'client_name': client_name,
            'client_discount': client_discount,
        }

		if 'preview_wash' in request.POST:
			return render(request, 'wash_demo.html', data)
		elif 'confirm_add_wash' in request.POST:
			wash = self.create_wash_object(shift.id, car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, services_price, services, washman_money)
			obj = Washman.objects.get(id=washman)
			obj.balance += washman_money
			obj.save()
			messages.success(request, 'Мойка успешно добавлена!')
			return redirect('add')

		return render(request, 'wash_demo.html', data)