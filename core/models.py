from django.db import models

#МОЙКА
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
	service = models.ManyToManyField("Service", blank=True, null=True, verbose_name="Услуги") 
	
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


class Consumption(models.Model):
	"""
	Модель БД для выплат
	"""
	id = models.AutoField(primary_key=True)
	shift = models.ForeignKey("Shift", on_delete=models.CASCADE, verbose_name="Смена", null=True, blank=True)
	washman = models.ForeignKey("Washman", on_delete=models.CASCADE, verbose_name="Мойщик")
	money = models.FloatField("Выплата", default=0)
	
	def __str__(self):
		return str(self.washman)
		
	class Meta:
		verbose_name = verbose_name_plural = "$Выплаты мойщикам"
		

class Stock(models.Model):
	"""
	Модель БД для склада
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField("Название", max_length=32, default="Не названа")
	quantity = models.IntegerField("Количество", default=0)
	price = models.IntegerField("Цена", default=0)
	is_visible = models.BooleanField("Видимость", default=False)
	
	def __str__(self):
		return self.name
		
	class Meta:
		verbose_name = verbose_name_plural = "#Склад"
		
		
class StockConsumption(models.Model):
	"""
	Модель БД для отчётности склада
	"""
	id = models.AutoField(primary_key=True)
	shift = models.ForeignKey("Shift", on_delete=models.CASCADE, verbose_name="Смена")
	stock = models.ForeignKey("Stock", on_delete=models.CASCADE, verbose_name="Предмет")
	quantity = models.IntegerField("Количество", default=0)
	money = models.IntegerField("Стоимость", default=0)
	pay = models.ForeignKey("Pay", on_delete=models.CASCADE, verbose_name="Тип оплаты")
	
	def __str__(self):
		return str(self.stock)
		
	class Meta:
		verbose_name = verbose_name_plural = "$Отчёты склада"
		
		
class OtherConsumption(models.Model):
	"""
	Модель БД ждя бытовых расходов
	"""
	id = models.AutoField(primary_key=True)
	shift = models.ForeignKey("Shift", on_delete=models.CASCADE, verbose_name="Смена")
	description = models.CharField("Описание", max_length=32, default="")
	money = models.IntegerField("Сумма", default=0)
	
	def __str__(self):
		return self.description
		
	class Meta:
		verbose_name = verbose_name_plural ="$Отчёты бытовые"
		
		
class RequestWash(models.Model):
	"""
	Модель для запросов на изменение моек
	"""
	obj = models.ForeignKey("Wash", on_delete=models.CASCADE, verbose_name="Мойка")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)
	
	def __str__(self):
		return str(self.obj)
		
	class Meta:
		verbose_name = verbose_name_plural = "'Запрос мойки"
		
		
class RequestStock(models.Model):
	"""
	Модель для запросов на изменение моек
	"""
	obj = models.ForeignKey("StockConsumption", on_delete=models.CASCADE, verbose_name="Приход")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)
	
	def __str__(self):
		return str(self.obj)
		
	class Meta:
		verbose_name = verbose_name_plural = "'Запрос склада"
		
		
class RequestConsumption(models.Model):
	"""
	Модель для запросов на изменение моек
	"""
	obj = models.ForeignKey("Consumption", on_delete=models.CASCADE, verbose_name="Расход")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)
	
	def __str__(self):
		return str(self.obj)
		
	class Meta:
		verbose_name = verbose_name_plural = "'Запрос расход"
		
		
class RequestOtherConsumption(models.Model):
	"""
	Модель для запросов на изменение моек
	"""
	obj = models.ForeignKey("OtherConsumption", on_delete=models.CASCADE, verbose_name="Расход")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)
	
	def __str__(self):
		return str(self.obj)
		
	class Meta:
		verbose_name = verbose_name_plural = "'Запрос бытовой расход"
		

class CarshService(models.Model):
	"""
	Модель для услуг каршеринга
	"""
	name = models.CharField("Название", max_length=32, default='Без имени')
	
	def __str__(self):
		return self.name
		
	class Meta:
		verbose_name = verbose_name_plural = ">Список услуг каршеринга"
		
		
class CarshCarClass(models.Model):
	"""
	Модель для классов авто каршеринга
	"""
	name = models.CharField('Название класса', max_length=32)
	
	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name = verbose_name_plural = "@Классы ТС каршеринга"
		
#ПРАЙС-ЛИСТЫ	
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
	
	
class CarshPriceList(models.Model):
	"""
	Модель для таблицы цен для каршеринга класс-услуга
	"""
	service = models.ForeignKey('CarshService', on_delete=models.CASCADE, verbose_name='Услуга')
	car_class = models.ForeignKey('CarshCarClass', on_delete=models.CASCADE, verbose_name='Класс авто')
	price = models.IntegerField('Стоимость')
	
	def __str__(self):
		return str(self.service)
		
	class Meta:
		verbose_name = verbose_name_plural = '%Прайс-лист каршеринга'	
		unique_together = [['service', 'car_class']]
	
	
class Settings(models.Model):
	"""
	Модель настроек
	"""
	name = models.CharField('Название', default='', max_length=32)
	admin_part = models.FloatField('Ставка администратора', default=0.0, help_text='Ставка администратора до преодоления порога кассы.')
	cash_treshhold = models.FloatField('Порог кассы', default=0.0, help_text='Порог кассы, после которого администратор начнёт получать процент с прибыли.')
	cash_treshhold_percent = models.FloatField('Процент порога', default=0.0, help_text='Процент который получит администратор при преодолении порога кассы. Пример: 0,5 = 50%')
	night_sale = models.FloatField('Ночная скидка', default=0.0, help_text='Скидка на ночные мойки. Пример: 0,5 = 50%')
	washman_percent = models.FloatField('Процент мойщика', default=0.0, help_text='Процет который получит мойщик с обычной мойки. Пример: 0,5 = 50%')
	washman_night_percent = models.FloatField('Ночной процент мойщика', default=0.0, help_text='Процент который получит мойщик с ночной мойки. Пример: 0,5 = 50%')
	washman_dry_percent = models.FloatField('Процент мойщика с химчистки', default=0.0, help_text='Процент который мойщик получает с химчисток. Пример: 0,5 = 50%')
	washman_poly_percent = models.FloatField('Процент мойщика с полировки', default=0.0, help_text='Процент который мойщик получает с полировки. Пример: 0,5 = 50%')
	is_active = models.BooleanField('Активность', default=False, help_text='Активность конфигурации')
	
	def save(self, *args, **kwargs):
		if self.is_active:
			Settings.objects.filter(is_active=True).update(is_active=False)
		super().save(*args, **kwargs)
        
	def __str__(self):
		return 'Настройки'
		
	class Meta:
		verbose_name = verbose_name_plural = 'Настрока'
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	