from django.contrib import admin

from .models import Coordinate


@admin.register(Coordinate)
class RestaurantAdmin(admin.ModelAdmin):
    fields = ['address', 'lat', 'lon', 'request_date']
