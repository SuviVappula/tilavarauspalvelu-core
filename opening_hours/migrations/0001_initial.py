# Generated by Django 3.0.10 on 2021-02-25 12:36

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import enumfields.fields
import opening_hours.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DatePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='Start date')),
                ('end_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='End date')),
                ('resource_state', enumfields.fields.EnumField(default='undefined', enum=opening_hours.enums.State, max_length=100, verbose_name='Resource state')),
                ('override', models.BooleanField(db_index=True, default=False, verbose_name='Override')),
            ],
            options={
                'verbose_name': 'Period',
                'verbose_name_plural': 'Periods',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='TimeSpanGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='time_span_groups', to='opening_hours.DatePeriod')),
            ],
        ),
        migrations.CreateModel(
            name='TimeSpan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_time', models.TimeField(blank=True, db_index=True, null=True, verbose_name='Start time')),
                ('end_time', models.TimeField(blank=True, db_index=True, null=True, verbose_name='End time')),
                ('end_time_on_next_day', models.BooleanField(default=False, verbose_name='Is end time on the next day')),
                ('full_day', models.BooleanField(default=False, verbose_name='24 hours')),
                ('weekdays', django.contrib.postgres.fields.ArrayField(base_field=enumfields.fields.EnumIntegerField(default=None, enum=opening_hours.enums.Weekday, verbose_name='Weekday'), blank=True, null=True, size=None)),
                ('resource_state', enumfields.fields.EnumField(default='undefined', enum=opening_hours.enums.State, max_length=100, verbose_name='Resource state')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='time_spans', to='opening_hours.TimeSpanGroup')),
            ],
            options={
                'verbose_name': 'Time span',
                'verbose_name_plural': 'Time spans',
                'ordering': ['weekdays', 'start_time', 'end_time_on_next_day', 'end_time', 'resource_state'],
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('context', enumfields.fields.EnumField(enum=opening_hours.enums.RuleContext, max_length=100, verbose_name='Context')),
                ('subject', enumfields.fields.EnumField(enum=opening_hours.enums.RuleSubject, max_length=100, verbose_name='Subject')),
                ('start', models.IntegerField(blank=True, null=True, verbose_name='Start')),
                ('frequency_ordinal', models.PositiveIntegerField(blank=True, null=True, verbose_name='Frequency (ordinal)')),
                ('frequency_modifier', enumfields.fields.EnumField(blank=True, enum=opening_hours.enums.FrequencyModifier, max_length=100, null=True, verbose_name='Frequency (modifier)')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rules', to='opening_hours.TimeSpanGroup')),
            ],
            options={
                'verbose_name': 'Rule',
                'verbose_name_plural': 'Rules',
            },
        ),
    ]
