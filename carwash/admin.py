from django.contrib import admin
from .models import *


@admin.register(Wash)
class WashAdmin(admin.ModelAdmin):
    list_display = ('grz', 'mark', 'car_class', 'washman', 'pay', 'price', 'time')
    list_filter = ('shift', 'car_class', 'washman', 'pay', 'night', 'dry', 'polishing')
    search_fields = ('grz', 'mark')


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('date',)
    date_hierarchy = 'date'


@admin.register(CarClass)
class CarClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Washman)
class WashmanAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'is_active')
    list_filter = ('is_active',)


@admin.register(Pay)
class PayAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(WashPriceList)
class WashPriceListAdmin(admin.ModelAdmin):
    list_display = ('service', 'car_class', 'price')
    list_filter = ('car_class', 'service')