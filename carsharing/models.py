from django.db import models


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