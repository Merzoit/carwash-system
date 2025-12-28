# Импорты моделей
try:
    from carwash.models import Shift, CarClass, Washman, Pay, Service, Wash, WashPriceList
    from warehouse.models import Stock, StockConsumption
    from system_settings.models import Settings
    from accounting.models import Consumption, OtherConsumption
except ImportError:
    # Для случаев когда приложения еще не импортированы
    pass


class Management():
	"""
	Управление движком
	"""
	def extract_data(self, request):
		# Извлечение данных из запроса
		# Возвращаем значения в порядке, в котором они встречаются в коде
		# Например:
		shift = Shift.objects.last().id
		car_class = request.POST.get('car_class') or request.POST.get('id_car_class')
		washman = request.POST.get('washman') or request.POST.get('id_washman')
		pay = request.POST.get('pay') or request.POST.get('id_pay')
		grz = request.POST.get('grz') or request.POST.get('id_grz')
		mark = request.POST.get('mark') or request.POST.get('id_mark')
		night = request.POST.get('night') == "on"
		dry = request.POST.get('dry') == "on"
		polishing = request.POST.get('polishing') == "on"
		sale = request.POST.get('sale') or request.POST.get('id_sale') or 0
		add = request.POST.get('add') or request.POST.get('id_add') or 0
		price = request.POST.get('price')
		return car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, price

	def get_selected_services(self, request):
		# Получение выбранных услуг из запроса
		service = [int(obj) for obj in request.POST.getlist('service')]
		services = Service.objects.filter(id__in=service)
		return services

	def calculate_services_price(self, services, car_class):
		# Алгоритм расчёта цены на основе выбранных услуг и класса автомобиля
		try:
			from carwash.models import WashPriceList
		except ImportError:
			return 0

		services_price = 0
		for obj in services:
			try:
				result = WashPriceList.objects.get(service=obj.id, car_class=car_class)
				services_price += result.price
			except WashPriceList.DoesNotExist:
				continue
		return services_price

	def get_settings(self):
		#Получение актуальных настроек
		try:
			from system_settings.models import Settings
		except ImportError:
			return None
		data = Settings.objects.filter(is_active=True).first()
		return data

	def apply_sale(self, services_price, sale):
		# Применение скидки к общей цене
		if sale != 0:
			services_price -= services_price * (int(sale) / 100)
		return services_price

	def apply_add(self, services_price, add):
		# Добавление дополнительной стоимости к общей цене
		services_price += int(add)
		return services_price

	def apply_night_discount(self, services_price, night, dry, polishing):
		# Применение скидки, если услуга ночного мытья выбрана без сушки и полировки
		settings = self.get_settings()
		if night and not dry and not polishing:
			services_price -= services_price * settings.night_sale
		return services_price

	def process_stock(self, stock, s_quantity):
		# Обработка данных о запасах
		try:
			from warehouse.models import Stock, StockConsumption
			from carwash.models import Shift
		except ImportError:
			return 0

		stock_price = 0
		if stock:
			item = Stock.objects.get(id=stock)
			stock_price += item.price * s_quantity
			item.quantity -= s_quantity
			item.save()
			consumption = StockConsumption.objects.create(
				shift=Shift.objects.last(),
				stock=Stock.objects.get(id=item.id),
				quantity=s_quantity,
				money=stock_price,
			)
		return stock_price

	def create_wash_object(self, shift, car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, services_price, services, washman_money):
		# Создание объекта Wash и его связей с другими моделями
		try:
			from carwash.models import Wash, Shift, CarClass, Washman, Pay
		except ImportError:
			return None

		wash = Wash.objects.create(
			shift=Shift.objects.get(id=shift),
			car_class=CarClass.objects.get(id=car_class),
			washman=Washman.objects.get(id=washman),
			pay=Pay.objects.get(id=pay),
			grz=grz,
			mark=mark,
			night=night,
			dry=dry,
			polishing=polishing,
			sale=sale,
			add=add,
			price=services_price,
			washman_money=washman_money,
		)
		wash.service.set(services)
		return wash


class Math():
	"""
	Вычисления статистики смены
	"""
	def wash_stock_price(self, stock_id, car_class):
		"""
		Расчёт баланса склада
		"""
		try:
			from carwash.models import Service
		except ImportError:
			return 0
		services = Service.objects.filter(id__in=stock_id)
		price = Management.calculate_services_price(self, services, car_class)
		return price

	def get_settings(self):
		#Получение актуальных настроек
		try:
			from system_settings.models import Settings
		except ImportError:
			return None
		data = Settings.objects.filter(is_active=True).first()
		return data

	def shift_balance(self, shift):
		"""
		Расчёт общего баланса смены
		"""
		try:
			from carwash.models import Wash
		except ImportError:
			return {"full": 0, "sale": 0}

		data = Wash.objects.filter(shift=shift)
		balance = 0
		sale_balance = 0
		for obj in data:
			if obj.sale == 0:
				balance += int(obj.price)
			else:
				balance += int(obj.price)
				sale_balance += int(obj.price) * int(obj.sale) / 100

		result = {
			"full": balance,
			"sale": balance + sale_balance
		}
		return result

	def shift_drop_balance(self, shift):
		"""
		Расчёт раздельного баланса смены по типам оплаты
		"""
		try:
			from warehouse.models import StockConsumption
			from carwash.models import Wash, Pay
		except ImportError:
			return {}

		data = Wash.objects.filter(shift=shift)
		data_stock = StockConsumption.objects.filter(shift=shift)

		# Получаем все типы оплаты
		all_pay_types = Pay.objects.all()
		result = {}

		# Инициализируем суммы для каждого типа оплаты
		for pay_type in all_pay_types:
			result[pay_type.name.lower()] = 0

		# Суммируем по мойкам
		for obj in data:
			pay_name = obj.pay.name.lower()
			if pay_name in result:
				result[pay_name] += obj.price

		# Суммируем по складу
		for obj in data_stock:
			pay_name = obj.pay.name.lower()
			if pay_name in result:
				result[pay_name] += obj.money

		return result

	def shift_washmans_consumption(self, shift):
		"""
		Расчёт расходов на зарплаты
		"""
		try:
			from accounting.models import Consumption
		except ImportError:
			return 0
		data = Consumption.objects.filter(shift=shift)
		result = 0
		for obj in data:
			result += obj.money
		return result

	def shift_other_consumption(self, shift):
		"""
		Расчёт бытовых расходов
		"""
		try:
			from accounting.models import OtherConsumption
		except ImportError:
			return 0
		data = OtherConsumption.objects.filter(shift=shift)
		result = 0
		for obj in data:
			result += obj.money
		return result

	def shift_stock_consumption(self, shift):
		"""
		Расчёт притока со склада
		"""
		try:
			from warehouse.models import StockConsumption
		except ImportError:
			return 0
		data = StockConsumption.objects.filter(shift=shift)
		result = 0
		for obj in data:
			result += obj.money
		return result

	def shift_admin_consumption(self, shift):
		"""
		Расчёт расходов на администратора
		"""
		try:
			from carwash.models import Wash
		except ImportError:
			return 0

		settings = self.get_settings()
		if not settings:
			return 0

		data = Wash.objects.filter(shift=shift)
		night_bank = 0
		result = 0
		for obj in data:
			if obj.night:
				night_bank += obj.price
		full_bank = self.shift_balance(shift)["sale"]
		result = full_bank - night_bank + self.shift_stock_consumption(shift=shift)

		# Рассчитываем ставку администратора
		if result <= settings.cash_treshhold:
			# Фиксированная ставка в рублях
			admin_payment = settings.admin_part
		else:
			# Фиксированная ставка + процент от превышения порога
			admin_payment = settings.admin_part + (result - settings.cash_treshhold) * settings.cash_treshhold_percent

		return round(admin_payment)
