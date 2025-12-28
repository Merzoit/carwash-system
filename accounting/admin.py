from django.contrib import admin
from .models import *


@admin.register(Consumption)
class ConsumptionAdmin(admin.ModelAdmin):
    list_display = ('washman', 'money', 'shift')
    list_filter = ('shift', 'washman')
    search_fields = ('washman__name',)


@admin.register(OtherConsumption)
class OtherConsumptionAdmin(admin.ModelAdmin):
    list_display = ('description', 'money', 'shift')
    list_filter = ('shift',)
    search_fields = ('description',)