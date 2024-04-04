# Generated by Django 3.2.15 on 2023-11-29 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20231129_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Наличностью'), ('card', 'Электронно')], db_index=True, default='Наличностью', max_length=50, verbose_name='Способ оплаты'),
        ),
    ]