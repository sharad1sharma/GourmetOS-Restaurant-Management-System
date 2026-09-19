from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'location', 'status')
    list_filter = ('status', 'location')
    list_editable = ('status',)
