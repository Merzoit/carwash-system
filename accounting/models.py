from django.db import models
from carwash.models import Shift, Washman


class Consumption(models.Model):
	"""
	Модель БД для выплат
	"""
	id = models.AutoField(primary_key=True)
	shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Смена", null=True, blank=True)
	washman = models.ForeignKey(Washman, on_delete=models.CASCADE, verbose_name="Мойщик")
	money = models.FloatField("Выплата", default=0)

	def __str__(self):
		return str(self.washman)

	class Meta:
		verbose_name = verbose_name_plural = "$Выплаты мойщикам"


class OtherConsumption(models.Model):
	"""
	Модель БД ждя бытовых расходов
	"""
	id = models.AutoField(primary_key=True)
	shift = models.ForeignKey(Shift, on_delete=models.CASCADE, verbose_name="Смена")
	description = models.CharField("Описание", max_length=32, default="")
	money = models.IntegerField("Сумма", default=0)

	def __str__(self):
		return self.description

	class Meta:
		verbose_name = verbose_name_plural ="$Отчёты бытовые"