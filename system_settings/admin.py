from django.contrib import admin
from .models import *


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'admin_part', 'cash_treshhold')
    list_filter = ('is_active',)