from django.contrib import admin
from .models import *


@admin.register(CarshService)
class CarshServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(CarshCarClass)
class CarshCarClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(CarshPriceList)
class CarshPriceListAdmin(admin.ModelAdmin):
    list_display = ('service', 'car_class', 'price')
    list_filter = ('car_class', 'service')