# Generated by Django 3.1.13 on 2021-11-09 10:57

from django.db import migrations


def migrate_reservation_purposes(apps, schema_editor):
    # Create reservation purposes based on the existing purposes
    Purpose = apps.get_model("reservation_units", "Purpose")
    ReservationPurpose = apps.get_model("reservations", "ReservationPurpose")
    db_alias = schema_editor.connection.alias
    purpose_map = {}
    for purpose in Purpose.objects.using(db_alias).all():
        reservation_purpose = ReservationPurpose.objects.create(
            name=purpose.name,
            name_fi=purpose.name_fi,
            name_sv=purpose.name_sv,
            name_en=purpose.name_en,
        )
        purpose_map[purpose.pk] = reservation_purpose.pk

    # For each reservation, make the purpose point to the new model
    OldReservationPurpose = apps.get_model("reservations", "OldReservationPurpose")
    for old_purpose in OldReservationPurpose.objects.using(db_alias).all():
        old_purpose.reservation.purpose_id = purpose_map[old_purpose.purpose.pk]
        old_purpose.reservation.save()

    Purpose.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0010_rename_reservation_purpose'),
    ]

    operations = [
        migrations.RunPython(migrate_reservation_purposes),
    ]
