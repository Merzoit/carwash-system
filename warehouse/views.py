from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from shared_algorythms import Management
from .models import Stock, StockConsumption
from carwash.models import Shift, Pay
from .forms import StockConsumptionForm


class WarehouseView(View):
    template_name = "warehouse.html"

    def get(self, request):
        context = {}
        context["stock_form"] = StockConsumptionForm()
        try:
            current_shift = Shift.objects.last()
            if current_shift:
                stock_consumptions = StockConsumption.objects.filter(shift=current_shift).order_by('-created_at')
                context["current_shift_stock_consumptions"] = stock_consumptions
                context["total_operations"] = stock_consumptions.count()
                context["total_consumption"] = sum(sc.money for sc in stock_consumptions)
            else:
                context["current_shift_stock_consumptions"] = []
                context["total_operations"] = 0
                context["total_consumption"] = 0
        except Shift.DoesNotExist:
            context["current_shift_stock_consumptions"] = []
            context["total_operations"] = 0
            context["total_consumption"] = 0

        # Добавляем данные об остатках товаров
        stock_items = Stock.objects.filter(is_visible=True).order_by('name')
        stock_balance = []
        for stock in stock_items:
            stock_balance.append({
                'id': stock.id,
                'name': stock.name,
                'quantity': stock.quantity,
                'price': stock.price,
                'total_value': stock.quantity * stock.price
            })
        context["stock_balance"] = stock_balance

        return render(request, self.template_name, context)


class AddStockView(View, Management):
    def post(self, request):
        shift = Shift.objects.last()

        # Extract data using Management's method or directly
        stock_id = request.POST.get("stock")
        quantity = request.POST.get("quantity") # Corrected field name
        pay_id = request.POST.get("pay")

        if not stock_id or not quantity or not pay_id:
            messages.error(request, 'Недостаточно данных для операции.')
            return render(request, 'stock_demo.html', {'error': 'Недостаточно данных'})

        try:
            stock_obj = Stock.objects.get(id=stock_id)
            pay_obj = Pay.objects.get(id=pay_id)
            stock_price = stock_obj.price
            quantity_int = int(quantity)

            # Проверяем, что количество товара не превышает остаток на складе
            if quantity_int > stock_obj.quantity:
                messages.error(request, f'Недостаточно товара на складе. Доступно: {stock_obj.quantity} шт.')
                return render(request, 'stock_demo.html', {'error': f'Недостаточно товара на складе. Доступно: {stock_obj.quantity} шт.'})

            price = quantity_int * stock_price
        except (Stock.DoesNotExist, Pay.DoesNotExist, ValueError) as e:
            messages.error(request, f'Ошибка данных: {e}')
            return render(request, 'stock_demo.html', {'error': f'Ошибка данных: {e}'})

        data = {
            'stock': stock_obj.name,
            'stock_id': stock_id, # Pass ID for form submission
            'stock_price': stock_price,
            'quantity': quantity_int,
            'pay': pay_obj.name,
            'pay_id': pay_id, # Pass ID for form submission
            'price': price,
        }

        if 'preview_stock' in request.POST:
            # Проверяем количество для preview
            if quantity_int > stock_obj.quantity:
                messages.error(request, f'Недостаточно товара на складе. Доступно: {stock_obj.quantity} шт.')
                # Возвращаем страницу склада с заполненной формой
                context = {
                    'stock_form': StockConsumptionForm(request.POST)
                }
                # Добавляем остальные данные как в WarehouseView
                try:
                    current_shift = Shift.objects.last()
                    if current_shift:
                        stock_consumptions = StockConsumption.objects.filter(shift=current_shift).order_by('-created_at')
                        context["current_shift_stock_consumptions"] = stock_consumptions
                        context["total_operations"] = stock_consumptions.count()
                        context["total_consumption"] = sum(sc.money for sc in stock_consumptions)
                    else:
                        context["current_shift_stock_consumptions"] = []
                        context["total_operations"] = 0
                        context["total_consumption"] = 0
                except Shift.DoesNotExist:
                    context["current_shift_stock_consumptions"] = []
                    context["total_operations"] = 0
                    context["total_consumption"] = 0

                # Добавляем данные об остатках товаров
                stock_items = Stock.objects.filter(is_visible=True).order_by('name')
                stock_balance = []
                for stock in stock_items:
                    stock_balance.append({
                        'id': stock.id,
                        'name': stock.name,
                        'quantity': stock.quantity,
                        'price': stock.price,
                        'total_value': stock.quantity * stock.price
                    })
                context["stock_balance"] = stock_balance

                return render(request, 'warehouse.html', context)
            return render(request, 'stock_demo.html', data)
        elif 'confirm_add_stock' in request.POST:
            try:
                pay_obj = Pay.objects.get(id=pay_id)
                stock_cons = StockConsumption.objects.create(
                    shift=shift,
                    stock=stock_obj,
                    quantity=quantity_int,
                    pay=pay_obj,
                    money=price,
                )

                stock_obj.quantity -= quantity_int
                stock_obj.save()
                messages.success(request, f'Складская операция успешно добавлена! Потрачено: {price} ₽')
                return redirect('warehouse')
            except Exception as e:
                return render(request, 'stock_demo.html', {'error': str(e)})

        return render(request, 'stock_demo.html', data)


class InventoryView(View):
	"""
	Управление инвентарем (складом)
	"""
	template_name = "inventory.html"

	def get(self, request):
		from .forms import StockForm

		context = {
			"stock_form": StockForm
		}

		# Получаем все товары на складе
		stocks = Stock.objects.all().order_by('name')
		# Добавляем расчет общей стоимости для каждого товара
		stocks_with_totals = []
		for stock in stocks:
			stock.total_value = stock.quantity * stock.price
			stocks_with_totals.append(stock)
		context["stocks"] = stocks_with_totals
		context["total_stocks"] = stocks.count()
		context["visible_stocks"] = stocks.filter(is_visible=True).count()
		context["hidden_stocks"] = stocks.filter(is_visible=False).count()

		# Статистика по складу
		total_value = sum(stock.quantity * stock.price for stock in stocks)
		low_stock_items = stocks.filter(quantity__lte=5, is_visible=True).count()
		out_of_stock_items = stocks.filter(quantity=0, is_visible=True).count()

		context["total_value"] = total_value
		context["low_stock_items"] = low_stock_items
		context["out_of_stock_items"] = out_of_stock_items

		return render(request, self.template_name, context)

	def post(self, request):
		from .forms import StockForm
		from django.contrib import messages

		if 'add_stock' in request.POST:
			form = StockForm(request.POST)
			if form.is_valid():
				try:
					stock = form.save()
					status = "видимый" if stock.is_visible else "скрытый"
					messages.success(request, f'Товар "{stock.name}" успешно добавлен на склад! Статус: {status}')
				except Exception as e:
					messages.error(request, f'Ошибка при добавлении товара: {str(e)}')
			else:
				messages.error(request, 'Ошибка в форме. Проверьте введенные данные.')

		elif 'update_stock' in request.POST:
			stock_id = request.POST.get('stock_id')
			try:
				stock = Stock.objects.get(id=stock_id)
				form = StockForm(request.POST, instance=stock)
				if form.is_valid():
					updated_stock = form.save()
					status = "видимый" if updated_stock.is_visible else "скрытый"
					messages.success(request, f'Товар "{updated_stock.name}" успешно обновлен! Статус: {status}')
				else:
					messages.error(request, 'Ошибка в форме обновления.')
			except Stock.DoesNotExist:
				messages.error(request, 'Товар не найден.')

		return redirect('inventory')