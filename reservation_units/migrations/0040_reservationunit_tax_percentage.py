# Generated by Django 3.1.14 on 2021-12-13 11:06

import django.db.models.deletion
from django.db import migrations, models

import reservation_units.models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_units', '0039_taxpercentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationunit',
            name='tax_percentage',
            field=models.ForeignKey(default=reservation_units.models.get_default_tax_percentage, help_text='The percentage of tax included in the price', on_delete=django.db.models.deletion.PROTECT, related_name='reservation_units', to='reservation_units.taxpercentage', verbose_name='Tax percentage'),
        ),
    ]
