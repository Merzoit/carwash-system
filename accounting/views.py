from django.views import View
from django.shortcuts import redirect
from .models import Consumption, OtherConsumption
from carwash.models import Shift, Washman


class AddConsView(View):
	"""
	Добавление выплаты
	"""
	def post(self, request):
		shift = Shift.objects.last()
		washman = request.POST.get("washman")
		money = request.POST.get("money")

		cons = Consumption.objects.create(
			shift=shift,
			washman=Washman.objects.get(id=washman),
			money=money,
			)
		man = Washman.objects.get(id=washman)
		man.balance -= int(money)
		man.save()
		return redirect(f"menu")


class AddOtherConsView(View):
	"""
	Добавление бытового расхода
	"""
	def post(self, request):
		shift = Shift.objects.last()
		description = request.POST.get("description")
		money = request.POST.get("money")

		other_cons = OtherConsumption.objects.create(
			shift=shift,
			description=description,
			money=money,
			)

		return redirect(f'menu')