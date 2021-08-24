# Generated by Django 3.1.13 on 2021-08-24 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaces', '0015_space_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='space',
            name='terms_of_use',
            field=models.TextField(blank=True, default='', max_length=2000, verbose_name='Terms of use'),
        ),
    ]
