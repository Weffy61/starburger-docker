from django.db import models
from django.utils import timezone


class Coordinate(models.Model):
    address = models.CharField(verbose_name='Адрес', unique=True, max_length=100, blank=True)
    lat = models.DecimalField(verbose_name='Широта', decimal_places=6, max_digits=9, blank=True, null=True)
    lon = models.DecimalField(verbose_name='Долгота', decimal_places=6, max_digits=9, blank=True, null=True)
    request_date = models.DateField(verbose_name='Дата запроса', default=timezone.now)

    class Meta:
        verbose_name = 'Координата'
        verbose_name_plural = 'Координаты'

    def __str__(self):
        return self.address
