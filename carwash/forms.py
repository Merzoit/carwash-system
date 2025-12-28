from django import forms
from .models import Wash, CarClass, Washman, Pay, Service, Client, WashPriceList
from warehouse.models import Stock


class AddWashForm(forms.ModelForm):
	"""
	Форма добавление бланка в базу
	"""
	stock = forms.ModelChoiceField(queryset=Stock.objects.all(), required=False)
	quant = forms.IntegerField(initial=0)

	class Meta:
		model = Wash
		fields = ('__all__')

	washman = forms.ModelChoiceField(
		queryset=Washman.objects.filter(is_active=True)
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		#Charfield
		self.fields['grz'].widget.attrs['class'] = 'form-control'
		self.fields['mark'].widget.attrs['class'] = 'form-control'
		self.fields['sale'].widget.attrs['class'] = 'form-control'
		self.fields['sale'].widget.attrs['min'] = 0
		self.fields['sale'].initial = 0  # Значение по умолчанию
		self.fields['quant'].widget.attrs['class'] = 'form-control'
		self.fields['price'].widget.attrs['class'] = 'form-control'
		self.fields['add'].widget.attrs['class'] = 'form-control'
		self.fields['price'].widget.attrs['readonly'] = 'readonly'
		#SelectField
		self.fields['car_class'].widget.attrs['class'] = 'form-select'
		self.fields['stock'].widget.attrs['class'] = 'form-select'
		self.fields['washman'].widget.attrs['class'] = 'form-select'
		#self.fields['wash_type'].widget.attrs['class'] = 'form-select'
		self.fields['shift'].widget.attrs['class'] = 'form-select'
		self.fields['pay'].widget.attrs['class'] = 'form-select'
		self.fields['service'].widget.attrs['class'] = 'form-select'
		#Other
		self.fields['service'].widget.attrs['size'] = '8'
		self.fields['service'].widget.attrs['aria-label'] = 'multiple'
		#CheckBox
		self.fields['dry'].widget.attrs['class'] = 'form-check-input'
		self.fields['night'].widget.attrs['class'] = 'form-check-input'
		self.fields['polishing'].widget.attrs['class'] = 'form-check-input'


class ClientForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования клиента
	"""
	class Meta:
		model = Client
		fields = ['license_plate', 'name', 'phone', 'discount']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['license_plate'].widget.attrs['class'] = 'form-control'
		self.fields['license_plate'].widget.attrs['placeholder'] = 'А000АА000'
		self.fields['license_plate'].widget.attrs['pattern'] = '[А-Яа-я0-9]{1,9}'
		self.fields['name'].widget.attrs['class'] = 'form-control'
		self.fields['name'].widget.attrs['placeholder'] = 'ФИО клиента'
		self.fields['phone'].widget.attrs['class'] = 'form-control'
		self.fields['phone'].widget.attrs['placeholder'] = '+7 (999) 123-45-67'
		self.fields['phone'].widget.attrs['type'] = 'tel'
		self.fields['discount'].widget.attrs['class'] = 'form-control'
		self.fields['discount'].widget.attrs['min'] = 0
		self.fields['discount'].widget.attrs['max'] = 100

	def clean_license_plate(self):
		license_plate = self.cleaned_data['license_plate'].upper()
		# Простая валидация гос номера
		if not license_plate.replace(' ', '').isalnum():
			raise forms.ValidationError("Гос номер может содержать только буквы и цифры")
		return license_plate


class WashmanForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования мойщика
	"""
	class Meta:
		model = Washman
		fields = ['name', 'balance', 'is_active']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs['class'] = 'form-control'
		self.fields['name'].widget.attrs['placeholder'] = 'Введите имя сотрудника'
		self.fields['balance'].widget.attrs['class'] = 'form-control'
		self.fields['balance'].widget.attrs['min'] = 0
		self.fields['balance'].widget.attrs['step'] = '0.01'
		self.fields['is_active'].widget.attrs['class'] = 'form-check-input'


class CarClassForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования классов ТС
	"""
	class Meta:
		model = CarClass
		fields = ['name']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs['class'] = 'form-control'
		self.fields['name'].widget.attrs['placeholder'] = 'Например: Легковой, Грузовой, Автобус'

	def clean_name(self):
		name = self.cleaned_data['name'].strip()
		if not name:
			raise forms.ValidationError("Название класса не может быть пустым")
		return name


class PayForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования типов оплаты
	"""
	class Meta:
		model = Pay
		fields = ['name']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs['class'] = 'form-control'
		self.fields['name'].widget.attrs['placeholder'] = 'Например: Наличные, Карта, Безналичный'

	def clean_name(self):
		name = self.cleaned_data['name'].strip()
		if not name:
			raise forms.ValidationError("Название типа оплаты не может быть пустым")
		return name


class ServiceForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования услуг
	"""
	class Meta:
		model = Service
		fields = ['name']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['name'].widget.attrs['class'] = 'form-control'
		self.fields['name'].widget.attrs['placeholder'] = 'Например: Базовая мойка, Полировка, Химчистка'

	def clean_name(self):
		name = self.cleaned_data['name'].strip()
		if not name:
			raise forms.ValidationError("Название услуги не может быть пустым")
		return name


class WashPriceListForm(forms.ModelForm):
	"""
	Форма для добавления/редактирования прайс-листа
	"""
	class Meta:
		model = WashPriceList
		fields = ['service', 'car_class', 'price']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['service'].widget.attrs['class'] = 'form-select'
		self.fields['car_class'].widget.attrs['class'] = 'form-select'
		self.fields['price'].widget.attrs['class'] = 'form-control'
		self.fields['price'].widget.attrs['min'] = 0
		self.fields['price'].widget.attrs['step'] = 0.01

	def clean_price(self):
		price = self.cleaned_data['price']
		if price <= 0:
			raise forms.ValidationError("Цена должна быть больше 0")
		return price
