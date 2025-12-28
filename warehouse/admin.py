from django.contrib import admin
from .models import *


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'price', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('name',)


@admin.register(StockConsumption)
class StockConsumptionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'quantity', 'money', 'pay', 'shift')
    list_filter = ('shift', 'pay')
    search_fields = ('stock__name',)