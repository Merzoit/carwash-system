from .models import *

class Management():
	"""
	Управление движком
	"""
	def extract_data(self, request):
		# Извлечение данных из запроса
		# Возвращаем значения в порядке, в котором они встречаются в коде
		# Например:
		shift = Shift.objects.last().id
		car_class = request.POST.get('car_class')
		washman = request.POST.get('washman')
		pay = request.POST.get('pay')
		grz = request.POST.get('grz')
		mark = request.POST.get('mark')
		night = True if request.POST.get('night') == "on" else False
		dry = True if request.POST.get('dry') == "on" else False
		polishing = True if request.POST.get('polishing') == "on" else False
		sale = request.POST.get('sale') or 0
		add = request.POST.get('add') or 0
		price = request.POST.get('price')
		return car_class, washman, pay, grz, mark, night, dry, polishing, sale, add, price

	def get_selected_services(self, request):
		# Получение выбранных услуг из запроса
		service = [int(obj) for obj in request.POST.getlist('service')]
		services = Service.objects.filter(id__in=service)
		return services
		
	def calculate_services_price(self, services, car_class):
		# Алгоритм расчёта цены на основе выбранных услуг и класса автомобиля
		services_price = 0
		for obj in services:
			try:
				result = WashPriceList.objects.get(service=obj.id, car_class=car_class)
				services_price += result.price
			except WashPriceList.DoesNotExist:
				continue
		return services_price

	'''	def calculate_services_price(self, services, car_class):
		# Алгоритм расчёта цены на основе выбранных услуг и класса автомобиля
		services_price = 0
		for obj in services:
			if car_class == "1":
				services_price += obj.price1
			elif car_class == "2":
				services_price += obj.price2
			elif car_class == "3":
				services_price += obj.price3
			else:
				services_price += obj.price4
		return services_price'''
	
	def get_settings(self):
		#Получение актуальных настроек
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
		services = Service.objects.filter(id__in=stock_id)
		price = Management.calculate_services_price(services, car_class)
		return price
	
	def get_settings(self):
		#Получение актуальных настроек
		data = Settings.objects.filter(is_active=True).first()
		return data
		
	def shift_balance(self, shift):
		"""
		Расчёт общего баланса смены
		"""
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
		Расчёт раздельного баланса смены
		"""
		data = Wash.objects.filter(shift=shift)
		data_stock = StockConsumption.objects.filter(shift=shift)
		balance_cash = 0
		balance_card = 0
		balance_online = 0
		for obj in data:
			if obj.pay.id == 1:
				balance_cash += obj.price
			elif obj.pay.id == 2:
				balance_card += obj.price
			elif obj.pay.id == 3:
				balance_online += obj.price
				
		for obj in data_stock:
			if obj.pay.id == 1:
				balance_cash += obj.money
			elif obj.pay.id == 2:
				balance_card += obj.money
			elif obj.pay.id == 3:
				balance_online += obj.money
		
		result = {
			"cash": balance_cash,
			"card": balance_card,
			"online": balance_online
		}
		return result
		
	def shift_washmans_consumption(self, shift):
		"""
		Расчёт расходов на зарплаты
		"""
		data = Consumption.objects.filter(shift=shift)
		result = 0
		for obj in data:
			result += obj.money
		return result
			
	def shift_other_consumption(self, shift):
		"""
		Расчёт бытовых расходов
		"""
		data = OtherConsumption.objects.filter(shift=shift)
		result = 0
		for obj in data:
			result += obj.money
		return result
		
	def shift_stock_consumption(self, shift):
		"""
		Расчёт притока со склада
		"""
		data = StockConsumption.objects.filter(shift=shift)
		result = 0
		for obj in data:
			result += obj.money
		return result
		
	def shift_admin_consumption(self, shift):
		"""
		Расчёт расходов на администратора
		"""
		settings = self.get_settings()
		data = Wash.objects.filter(shift=shift)
		night_bank = 0
		result = 0
		for obj in data:
			if obj.night:
				night_bank += obj.price
		full_bank = self.shift_balance(shift)["sale"]
		result = full_bank - night_bank + self.shift_stock_consumption(shift=shift)
		if result <= settings.cash_treshhold:
			return settings.admin_part
		else:
			return round(settings.admin_part + (result - settings.cash_treshhold) * settings.cash_treshhold_percent)