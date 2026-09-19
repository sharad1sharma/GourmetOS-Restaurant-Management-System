from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'table', 'party_size', 'reservation_time', 'status')
    list_filter = ('status',)
    search_fields = ('customer_name', 'customer_phone')
    date_hierarchy = 'reservation_time'
