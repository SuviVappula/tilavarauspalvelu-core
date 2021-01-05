# Generated by Django 3.0.10 on 2021-01-07 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_units', '0005_purposes_field_to_res_units'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
        ),
        migrations.AddField(
            model_name='reservationunit',
            name='terms_of_use',
            field=models.TextField(blank=True, max_length=2000, verbose_name='Terms of use'),
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment', to='reservation_units.EquipmentCategory', verbose_name='Category')),
            ],
        ),
        migrations.AddField(
            model_name='reservationunit',
            name='equipments',
            field=models.ManyToManyField(blank=True, to='reservation_units.Equipment', verbose_name='Equipments'),
        ),
    ]
