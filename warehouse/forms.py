from django import forms
from .models import StockConsumption, Stock
from carwash.models import Pay


class StockConsumptionForm(forms.ModelForm):
	"""
	Форма для складских операций
	"""
	class Meta:
		model = StockConsumption
		fields = ('stock', 'quantity', 'pay')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Показываем только видимые товары
		self.fields['stock'].queryset = Stock.objects.filter(is_visible=True)
		# Настройка виджетов
		self.fields['stock'].widget.attrs['class'] = 'form-select'
		self.fields['quantity'].widget.attrs['class'] = 'form-control'
		self.fields['quantity'].widget.attrs['min'] = 1
		self.fields['pay'].widget.attrs['class'] = 'form-select'


class StockForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования товара на складе
	"""
	class Meta:
		model = Stock
		fields = ['name', 'quantity', 'price', 'is_visible']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs['class'] = 'form-control'
		self.fields['name'].widget.attrs['placeholder'] = 'Название товара'
		self.fields['quantity'].widget.attrs['class'] = 'form-control'
		self.fields['quantity'].widget.attrs['min'] = 0
		self.fields['quantity'].widget.attrs['step'] = 1
		self.fields['price'].widget.attrs['class'] = 'form-control'
		self.fields['price'].widget.attrs['min'] = 0
		self.fields['price'].widget.attrs['step'] = 0.01
		self.fields['is_visible'].widget.attrs['class'] = 'form-check-input'

	def clean_name(self):
		name = self.cleaned_data['name'].strip()
		if not name:
			raise forms.ValidationError("Название товара не может быть пустым")
		return name

	def clean_quantity(self):
		quantity = self.cleaned_data['quantity']
		if quantity < 0:
			raise forms.ValidationError("Количество не может быть отрицательным")
		return quantity

	def clean_price(self):
		price = self.cleaned_data['price']
		if price < 0:
			raise forms.ValidationError("Цена не может быть отрицательной")
		return price


