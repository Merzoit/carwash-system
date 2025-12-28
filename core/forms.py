from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import *


class LoginForm(AuthenticationForm):
	"""
	Форма авторизации
	"""
	model = User
	fields = ("username", "password")
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["username"].widget.attrs["class"] = "form-control"
		self.fields["password"].widget.attrs["class"] = "form-control"
		
		
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
		self.fields['quant'].widget.attrs['class'] = 'form-control'
		self.fields['sale'].widget.attrs['min'] = 0
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
		fields = ("__all__")
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
		self.fields["description"].widget.attrs['class'] = 'form-control field-center'
		self.fields["money"].widget.attrs['class'] = 'form-control field-center'


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
		
	
class AddRequestWashForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение мойки
	"""
	class Meta:
		model = RequestWash
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
		self.fields["description"].widget.attrs['class'] = 'form-control'
		
		
class AddRequestStockForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение мойки
	"""
	class Meta:
		model = RequestStock
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
		self.fields["description"].widget.attrs['class'] = 'form-control'


class AddRequestConsumptionForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение мойки
	"""
	class Meta:
		model = RequestConsumption
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
		self.fields["description"].widget.attrs['class'] = 'form-control'
		
		
class AddRequestOtherConsumptionForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение мойки
	"""
	class Meta:
		model = RequestOtherConsumption
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
		self.fields["description"].widget.attrs['class'] = 'form-control'


class AddCarClassForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение мойки
	"""
	class Meta:
		model = CarClass
		fields = ("name",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)	
		self.fields["name"].widget.attrs['class'] = 'form-control'