from django.contrib import admin
from .models import *


@admin.register(RequestWash)
class RequestWashAdmin(admin.ModelAdmin):
    list_display = ('obj', 'description', 'is_active')
    list_filter = ('is_active',)


@admin.register(RequestStock)
class RequestStockAdmin(admin.ModelAdmin):
    list_display = ('obj', 'description', 'is_active')
    list_filter = ('is_active',)


@admin.register(RequestConsumption)
class RequestConsumptionAdmin(admin.ModelAdmin):
    list_display = ('obj', 'description', 'is_active')
    list_filter = ('is_active',)


@admin.register(RequestOtherConsumption)
class RequestOtherConsumptionAdmin(admin.ModelAdmin):
    list_display = ('obj', 'description', 'is_active')
    list_filter = ('is_active',)