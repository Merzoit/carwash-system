from django import forms
from .models import RequestWash, RequestStock, RequestConsumption, RequestOtherConsumption


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
	Форма для добавления запросов на изменение склада
	"""
	class Meta:
		model = RequestStock
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["description"].widget.attrs['class'] = 'form-control'


class AddRequestConsumptionForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение расходов
	"""
	class Meta:
		model = RequestConsumption
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["description"].widget.attrs['class'] = 'form-control'


class AddRequestOtherConsumptionForm(forms.ModelForm):
	"""
	Форма для добавления запросов на изменение бытовых расходов
	"""
	class Meta:
		model = RequestOtherConsumption
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["description"].widget.attrs['class'] = 'form-control'


