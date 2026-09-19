from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('unit_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'order_type', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'order_type')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
