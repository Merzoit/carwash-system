from django.db import models


class Shift(models.Model):
	"""
	Модель БД для объектов смен
	"""
	id = models.AutoField(primary_key=True)
	date = models.DateField("Дата", unique=True)

	def __str__(self):
		return f"{self.date}"

	class Meta:
		verbose_name = verbose_name_plural = "#Список смен"


class CarClass(models.Model):
	"""
	Модель БД для объектов класса авто
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField("Название класса", max_length=32)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = verbose_name_plural = "@Классы ТС мойки"


class Washman(models.Model):
	"""
	Модель БД для объектов мойщиков
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField("Имя", max_length=64)
	balance = models.IntegerField("Баланс", default=0)
	is_active = models.BooleanField("Активность", default="True")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = verbose_name_plural = "#Список мойщиков"


class Pay(models.Model):
	"""
	Модель БД для объектов типа оплаты
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField("Тип", max_length=32)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = verbose_name_plural = ">Типы оплаты"


class Service(models.Model):
	"""
	Модель БД для услуг мойки
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField("Название", max_length=32, default="Без имени")

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = verbose_name_plural = ">Список услуг мойки"


class Wash(models.Model):
	"""
	Модель БД для объектов мойки
	"""
	id = models.AutoField(primary_key=True)
	time = models.TimeField("Время", auto_now_add=True)
	shift = models.ForeignKey("Shift", on_delete=models.CASCADE, verbose_name="Смена")
	car_class = models.ForeignKey("CarClass", on_delete=models.CASCADE, verbose_name="Класс авто")
	washman = models.ForeignKey("Washman", on_delete=models.CASCADE, verbose_name="Мойщик")
	pay = models.ForeignKey("Pay", on_delete=models.CASCADE, verbose_name="Тип оплаты")
	service = models.ManyToManyField("Service", blank=True, verbose_name="Услуги")

	grz = models.CharField("ГРЗ", max_length=9, default="а000аа000")
	mark = models.CharField("Марка", max_length=32, default="Марка")

	night = models.BooleanField("Ночная", default=False)
	dry = models.BooleanField("Химчистка", default=False)
	polishing = models.BooleanField("Полировка", default=False)

	sale = models.PositiveIntegerField("Скидка", default=0)
	add = models.IntegerField("Добавочная стоимость", default=0)
	price = models.IntegerField("Цена", default=0)

	washman_money = models.FloatField("Процент мойщика", default=0)

	def __str__(self):
		return self.grz

	class Meta:
		verbose_name = verbose_name_plural = "#Список моек"


class WashPriceList(models.Model):
	"""
	Модель для таблицы цен для мойки класс-услуга
	"""
	service = models.ForeignKey('Service', on_delete=models.CASCADE, verbose_name='Услуга')
	car_class = models.ForeignKey('CarClass', on_delete=models.CASCADE, verbose_name='Класс авто')
	price = models.IntegerField('Стоимость')

	def __str__(self):
		return str(self.service)

	class Meta:
		verbose_name = verbose_name_plural = '%Прайс-лист мойки'
		unique_together = [['service', 'car_class']]


class Client(models.Model):
	"""
	Модель БД для клиентов автомойки
	"""
	id = models.AutoField(primary_key=True)
	license_plate = models.CharField("Государственный номер", max_length=9, unique=True)
	name = models.CharField("Имя клиента", max_length=100)
	phone = models.CharField("Номер телефона", max_length=20, blank=True, null=True)
	discount = models.IntegerField("Скидка (%)", default=0, help_text="Процент скидки для клиента")

	def __str__(self):
		return f"{self.name} ({self.license_plate})"

	class Meta:
		verbose_name = "Клиент"
		verbose_name_plural = "Клиенты"
		ordering = ['name']