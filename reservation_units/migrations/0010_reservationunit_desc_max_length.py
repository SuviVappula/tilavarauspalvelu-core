# Generated by Django 3.0.10 on 2021-03-09 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_units', '0009_reservationunit_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationunit',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Description'),
        ),
    ]
