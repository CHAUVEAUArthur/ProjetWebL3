from django.contrib import admin

# Register your models here.
# filepath: /Users/hassanjatta/Library/Mobile Documents/com~apple~CloudDocs/MIAGE/ProjetWebL3/mySiteWeb/app1/admin.py
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'room', 'participants')
    list_filter = ('room', 'start_time', 'end_time')
    search_fields = ('user__username', 'room')
    ordering = ('start_time',)