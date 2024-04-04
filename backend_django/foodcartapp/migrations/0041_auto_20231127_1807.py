# Generated by Django 3.2.15 on 2023-11-27 18:07

from django.db import migrations


def fill_item_price(apps, schema_editor):
    OrderItem = apps.get_model('foodcartapp', 'OrderItem')

    for item in OrderItem.objects.all().iterator():
        item.price = item.product.price
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderitem_price'),
    ]

    operations = [
        migrations.RunPython(fill_item_price)
    ]