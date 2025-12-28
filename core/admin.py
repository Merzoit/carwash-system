from django.contrib import admin
from .models import *
from django.contrib.admin import DateFieldListFilter
from rangefilter.filters import DateRangeFilter


class WashAdmin(admin.ModelAdmin):
	list_display = ('id','shift', 'time', 'grz', 'mark', 'washman', 'pay', 'sale', 'price', 'service_list', 'night', 'dry', 'polishing')
	list_filter = (('shift__date', DateRangeFilter), 'pay', 'washman', 'service', 'night', 'dry', 'polishing')
	search_fields = ('id', 'grz', 'mark',)
	list_display_links = ('grz',)
	

	def service_list(self, obj):
		return ", ".join([str(service) for service in obj.service.all()])
	service_list.short_description = 'Service'
    
	def delete_model(self, request, obj):
		washman = Washman.objects.get(id=obj.washman.id)
		money = obj.washman_money
		washman.balance -= money
		washman.save()
		super().delete_model(request, obj)
	
	def delete_queryset(self, request, queryset):
		for obj in queryset:
			washman = Washman.objects.get(id=obj.washman.id)
			money = obj.washman_money
			washman.balance -= money
			washman.save()
		super().delete_queryset(request, queryset)
		
class CarClassAdmin(admin.ModelAdmin):
	 list_display = ('id', 'name')
	 search_fields = ('id', 'name',)


class WashmanAdmin(admin.ModelAdmin):
	list_display = ("name", "balance", "is_active")
	search_fields = ('name',)


class ServiceAdmin(admin.ModelAdmin):
	list_display = ("name")
	search_fields = ('name',)


class ConsumptionAdmin(admin.ModelAdmin):
	list_display = ("shift", "washman", "money") 
	search_fields = ("washman", "shift__date")
	list_filter = (("shift__date", DateRangeFilter), "washman")
	
	def delete_model(self, request, obj):
		try:
			washman = Washman.objects.get(id=obj.washman.id)
			money = obj.money
			washman.balance += obj.money
			washman.save()
		except Washman.DoesNotExist:
			print(f"Washman with id {obj.washman.id} does not exist.")
		except Exception as e:
			print(f"An error occurred: {str(e)}")
		super().delete_model(request, obj)
		
	def delete_queryset(self, request, queryset):
		for obj in queryset:
			washman = Washman.objects.get(id=obj.washman.id)
			money = obj.money
			washman.balance += money
			washman.save()
		super().delete_queryset(request, queryset)


class StockAdmin(admin.ModelAdmin):
	list_display = ("name", "quantity", "price")
	search_fields = ("name",)


class StockConsumptionAdmin(admin.ModelAdmin):
	list_display = ("shift", "stock", "quantity", "pay", "money")
	search_fields = ("stock", "shift__date")
	list_filter = (("shift__date", DateRangeFilter), "pay", "stock__name")
	
	def delete_model(self, request, obj):
		stock = Stock.objects.get(id=obj.stock.id)
		quantity = obj.quantity
		stock.quantity += quantity
		stock.save()
		super().delete_model(request, obj)
		
	def delete_queryset(self, request, queryset):
		for obj in queryset:
			stock = Stock.objects.get(id=obj.stock.id)
			quantity = obj.quantity
			stock.quantity += quantity
			stock.save()
		super().delete_queryset(request, queryset)
	
class WashPriceListAdmin(admin.ModelAdmin):
	list_display = ("service", "car_class", "price")
	search_fields = ("service", "car_class",)
	list_filter = ("service", "car_class")
	
admin.site.register(Wash, WashAdmin)
admin.site.register(Shift)
admin.site.register(CarClass, CarClassAdmin)
admin.site.register(Washman, WashmanAdmin)
admin.site.register(Pay)
admin.site.register(Service)
admin.site.register(Consumption, ConsumptionAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(StockConsumption, StockConsumptionAdmin)
admin.site.register(OtherConsumption)
admin.site.register(RequestWash)
admin.site.register(RequestStock)
admin.site.register(RequestConsumption)
admin.site.register(RequestOtherConsumption)
admin.site.register(WashPriceList, WashPriceListAdmin)
admin.site.register(CarshPriceList)
admin.site.register(CarshService)
admin.site.register(CarshCarClass)
admin.site.register(Settings)

