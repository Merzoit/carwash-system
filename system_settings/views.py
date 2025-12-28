from django.views import View
from django.shortcuts import render, redirect
from .models import Settings
from .forms import AddShiftForm
from carwash.models import Shift


class AddShiftView(View):
	"""
	Открытие смены
	"""
	def post(self, request):
		shift_form = AddShiftForm(request.POST)
		if shift_form.is_valid():
			shift_form.save()
			return redirect('menu')

		return render(request, 'menu.html', {'shift_form': shift_form})