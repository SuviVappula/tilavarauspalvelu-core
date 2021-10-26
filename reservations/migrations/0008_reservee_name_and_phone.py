# Generated by Django 3.1.13 on 2021-10-26 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0007_reservation_name_and_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='reservee_name',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Reservee name'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='reservee_phone',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Reservee phone'),
        ),
    ]
