from django.db import models
from django.utils import timezone
from carwash.models import Shift, Pay


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
	shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Смена")
	stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="Предмет")
	quantity = models.IntegerField("Количество", default=0)
	money = models.IntegerField("Стоимость", default=0)
	pay = models.ForeignKey(Pay, on_delete=models.CASCADE, verbose_name="Тип оплаты")
	created_at = models.DateTimeField("Время создания", default=timezone.now)

	def __str__(self):
		return str(self.stock)

	class Meta:
		verbose_name = verbose_name_plural = "$Отчёты склада"