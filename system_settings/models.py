from django.db import models


class Settings(models.Model):
	"""
	Модель настроек
	"""
	name = models.CharField('Название', default='', max_length=32)
	admin_part = models.IntegerField('Ставка администратора', default=0, help_text='Фиксированная ставка администратора в рублях до преодоления порога кассы.')
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
		verbose_name = verbose_name_plural = 'Настройки'