from django import forms
from .models import Consumption, OtherConsumption


class AddConsForm(forms.ModelForm):
	"""
	Форма добавления выплаты в базу
	"""
	class Meta:
		model = Consumption
		fields = ("__all__")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["washman"].widget.attrs['class'] = 'form-select field-center'
		self.fields["money"].widget.attrs['class'] = 'form-control field-center'


class AddOtherConsForm(forms.ModelForm):
	"""
	Форма добавления бытовых расходов
	"""
	class Meta:
		model = OtherConsumption
		fields = ("description", "money")  # Исключаем shift, он будет установлен в представлении

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["description"].widget.attrs['class'] = 'form-control'
		self.fields["description"].widget.attrs['placeholder'] = 'Например: Интернет, Мусорные пакеты'
		self.fields["money"].widget.attrs['class'] = 'form-control'
		self.fields["money"].widget.attrs['min'] = 1
		self.fields["money"].widget.attrs['step'] = '0.01'


