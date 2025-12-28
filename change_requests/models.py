from django.db import models
from carwash.models import Wash
from warehouse.models import StockConsumption
from accounting.models import Consumption, OtherConsumption


class RequestWash(models.Model):
	"""
	Модель для запросов на изменение моек
	"""
	obj = models.ForeignKey(Wash, on_delete=models.CASCADE, verbose_name="Мойка")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)

	def __str__(self):
		return str(self.obj)

	class Meta:
		verbose_name = verbose_name_plural = "'Запрос мойки"


class RequestStock(models.Model):
	"""
	Модель для запросов на изменение склада
	"""
	obj = models.ForeignKey(StockConsumption, on_delete=models.CASCADE, verbose_name="Приход")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)

	def __str__(self):
		return str(self.obj)

	class Meta:
		verbose_name = verbose_name_plural = "'Запрос склада"


class RequestConsumption(models.Model):
	"""
	Модель для запросов на изменение расходов
	"""
	obj = models.ForeignKey(Consumption, on_delete=models.CASCADE, verbose_name="Расход")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)

	def __str__(self):
		return str(self.obj)

	class Meta:
		verbose_name = verbose_name_plural = "'Запрос расход"


class RequestOtherConsumption(models.Model):
	"""
	Модель для запросов на изменение бытовых расходов
	"""
	obj = models.ForeignKey(OtherConsumption, on_delete=models.CASCADE, verbose_name="Расход")
	description = models.TextField("Описание", default="")
	is_active = models.BooleanField("Активна", default=True)

	def __str__(self):
		return str(self.obj)

	class Meta:
		verbose_name = verbose_name_plural = "'Запрос бытовой расход"