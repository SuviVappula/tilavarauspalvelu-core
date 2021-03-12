# Generated by Django 3.1.7 on 2021-03-12 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_change_general_role_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalrolepermission',
            name='permission',
            field=models.CharField(choices=[('can_manage_general_roles', 'Can manage general roles for the whole system'), ('can_manage_service_sector_roles', 'Can manage roles for service sectorsfor the whole system'), ('can_manage_unit_roles', 'Can manage roles for units in the whole system'), ('can_manage_reservation_units', 'Can create, edit and delete reservation units in the whole system'), ('can_manage_purposes', 'Can create, edit and delete purposes in the whole system'), ('can_manage_age_groups', 'Can create, edit and delete age groups in the whole system'), ('can_manage_districts', 'Can create, edit and delete districts in the whole system'), ('can_manage_ability_groups', 'Can create, edit and delete ability groups in the whole system'), ('can_manage_reservation_unit_types', 'Can create, edit and delete reservation unit types in the whole system'), ('can_manage_equipment_categories', 'Can create, edit and delete equipment_categories in the whole system'), ('can_manage_equipment', 'Can create, edit and delete equipment in the whole system'), ('can_view_reservations', 'Can create, edit and delete equipment in the whole system'), ('can_manage_reservations', 'Can create, edit and delete equipment in the whole system'), ('can_manage_reservations', 'Can create, edit and cancel reservations in the whole system'), ('can_view_reservations', 'Can view details of all reservations in the whole system'), ('can_manage_resources', 'Can create, edit and delete resources in the whole system'), ('can_handle_applications', 'Can handle applications in the whole system'), ('can_manage_application_rounds', 'Can create, edit and delete application rounds in the whole system'), ('can_view_users', 'Can view users in the whole system')], max_length=255, verbose_name='Permission'),
        ),
        migrations.AlterField(
            model_name='servicesectorrolepermission',
            name='permission',
            field=models.CharField(choices=[('can_manage_service_sector_roles', 'Can modify roles for the service sector'), ('can_manage_unit_roles', 'Can modify roles for units in the service sector'), ('can_manage_reservation_units', 'Can create, edit and delete reservation units in certain unit'), ('can_manage_application_rounds', 'Can create, edit and delete application rounds in the service sector'), ('can_handle_applications', 'Can handle applications in the service sector'), ('can_manage_reservations', 'Can create, edit and cancel reservations in the service sector'), ('can_view_reservations', 'Can view details of all reservations in the service sector'), ('can_view_users', 'Can view users in the whole system')], max_length=255, verbose_name='Permission'),
        ),
        migrations.AlterField(
            model_name='unitrolepermission',
            name='permission',
            field=models.CharField(choices=[('can_manage_unit_roles', 'Can modify roles for the unit'), ('can_manage_reservation_units', 'Can create, edit and delete reservation units in the unit'), ('can_manage_reservations', 'Can create, edit and cancel reservations in the unit'), ('can_view_reservations', 'Can view details of all reservations in the unit'), ('can_view_users', 'Can view users in the whole system')], max_length=255, verbose_name='Permission'),
        ),
    ]
