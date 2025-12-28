from django import forms
from .models import Settings
from carwash.models import Shift, CarClass


class SystemSettingsForm(forms.ModelForm):
	"""
	Форма для системных настроек
	"""
	class Meta:
		model = Settings
		fields = [
			'name', 'admin_part', 'cash_treshhold', 'cash_treshhold_percent',
			'night_sale', 'washman_percent', 'washman_night_percent',
			'washman_dry_percent', 'washman_poly_percent', 'is_active'
		]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Настройка виджетов
		self.fields['name'].widget.attrs.update({
			'class': 'form-control',
			'placeholder': 'Название конфигурации'
		})
		self.fields['admin_part'].widget.attrs.update({
			'class': 'form-control',
			'step': '1',
			'min': '0'
		})
		self.fields['cash_treshhold'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0'
		})
		self.fields['cash_treshhold_percent'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0',
			'max': '1'
		})
		self.fields['night_sale'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0',
			'max': '1'
		})
		self.fields['washman_percent'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0',
			'max': '1'
		})
		self.fields['washman_night_percent'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0',
			'max': '1'
		})
		self.fields['washman_dry_percent'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0',
			'max': '1'
		})
		self.fields['washman_poly_percent'].widget.attrs.update({
			'class': 'form-control',
			'step': '0.01',
			'min': '0',
			'max': '1'
		})
		self.fields['is_active'].widget.attrs.update({
			'class': 'form-check-input'
		})

	def clean_admin_part(self):
		admin_part = self.cleaned_data.get('admin_part')
		if admin_part < 0:
			raise forms.ValidationError('Ставка администратора не может быть отрицательной')
		return admin_part

	def clean_cash_treshhold_percent(self):
		percent = self.cleaned_data.get('cash_treshhold_percent')
		if percent < 0 or percent > 1:
			raise forms.ValidationError('Процент порога должен быть от 0 до 1 (0% до 100%)')
		return percent

	def clean_night_sale(self):
		night_sale = self.cleaned_data.get('night_sale')
		if night_sale < 0 or night_sale > 1:
			raise forms.ValidationError('Ночная скидка должна быть от 0 до 1 (0% до 100%)')
		return night_sale

	def clean_washman_percent(self):
		percent = self.cleaned_data.get('washman_percent')
		if percent < 0 or percent > 1:
			raise forms.ValidationError('Процент мойщика должен быть от 0 до 1 (0% до 100%)')
		return percent

	def clean_washman_night_percent(self):
		percent = self.cleaned_data.get('washman_night_percent')
		if percent < 0 or percent > 1:
			raise forms.ValidationError('Ночной процент мойщика должен быть от 0 до 1 (0% до 100%)')
		return percent

	def clean_washman_dry_percent(self):
		percent = self.cleaned_data.get('washman_dry_percent')
		if percent < 0 or percent > 1:
			raise forms.ValidationError('Процент мойщика с химчистки должен быть от 0 до 1 (0% до 100%)')
		return percent

	def clean_washman_poly_percent(self):
		percent = self.cleaned_data.get('washman_poly_percent')
		if percent < 0 or percent > 1:
			raise forms.ValidationError('Процент мойщика с полировки должен быть от 0 до 1 (0% до 100%)')
		return percent


class AddShiftForm(forms.ModelForm):
	"""
	Форма добавления смены
	"""
	class Meta:
		model = Shift
		fields = "__all__"
		widgets = {
			'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
		}


class AddCarClassForm(forms.ModelForm):
	"""
	Форма для добавления класса автомобиля
	"""
	class Meta:
		model = CarClass
		fields = ("name",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["name"].widget.attrs['class'] = 'form-control'


