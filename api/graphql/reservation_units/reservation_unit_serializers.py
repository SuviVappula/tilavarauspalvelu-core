from rest_framework import serializers

from api.graphql.base_serializers import (
    PrimaryKeySerializer,
    PrimaryKeyUpdateSerializer,
)
from api.graphql.translate_fields import get_all_translatable_fields
from api.reservation_units_api import (
    EquipmentCategorySerializer,
    EquipmentSerializer,
    ReservationUnitSerializer,
)
from reservation_units.models import (
    Equipment,
    Purpose,
    ReservationUnit,
    ReservationUnitType,
    EquipmentCategory,
)
from resources.models import Resource
from services.models import Service
from spaces.models import Space, Unit


class EquipmentCreateSerializer(EquipmentSerializer, PrimaryKeySerializer):
    category_pk = serializers.PrimaryKeyRelatedField(
        queryset=EquipmentCategory.objects.all(), source="category"
    )

    class Meta(EquipmentSerializer.Meta):
        fields = [
            "id",
            "category_pk",
        ] + get_all_translatable_fields(EquipmentSerializer.Meta.model)

    def validate(self, data):
        name_fi = data.get("name_fi", getattr(self.instance, "name_fi", None))
        no_name_fi = not name_fi or name_fi.isspace()
        if no_name_fi:
            raise serializers.ValidationError("nameFi is required.")

        return data


class EquipmentUpdateSerializer(PrimaryKeyUpdateSerializer, EquipmentCreateSerializer):
    class Meta(EquipmentCreateSerializer.Meta):
        fields = EquipmentCreateSerializer.Meta.fields + ["pk"]


class EquipmentCategoryCreateSerializer(
    EquipmentCategorySerializer, PrimaryKeySerializer
):
    class Meta(EquipmentCategorySerializer.Meta):
        fields = ["id"] + get_all_translatable_fields(EquipmentSerializer.Meta.model)

    def validate(self, data):
        name_fi = data.get("name_fi", getattr(self.instance, "name_fi", None))
        no_name_fi = not name_fi or name_fi.isspace()
        if no_name_fi:
            raise serializers.ValidationError("nameFi is required.")

        return data


class EquipmentCategoryUpdateSerializer(
    PrimaryKeyUpdateSerializer, EquipmentCategoryCreateSerializer
):
    class Meta(EquipmentCategoryCreateSerializer.Meta):
        fields = EquipmentCategoryCreateSerializer.Meta.fields + ["pk"]


class PurposeCreateSerializer(PrimaryKeySerializer):
    class Meta:
        model = Purpose
        fields = get_all_translatable_fields(model)


class PurposeUpdateSerializer(PrimaryKeyUpdateSerializer, PurposeCreateSerializer):
    class Meta(PurposeCreateSerializer.Meta):
        fields = ["pk"] + PurposeCreateSerializer.Meta.fields


class ReservationUnitCreateSerializer(ReservationUnitSerializer, PrimaryKeySerializer):
    terms_of_use_fi = serializers.CharField(required=False)
    terms_of_use_sv = serializers.CharField(required=False)
    terms_of_use_en = serializers.CharField(required=False)
    name_fi = serializers.CharField(required=False, allow_blank=True)
    name_sv = serializers.CharField(required=False, allow_blank=True)
    name_en = serializers.CharField(required=False, allow_blank=True)
    max_reservation_duration = serializers.DurationField(required=False)
    min_reservation_duration = serializers.DurationField(required=False)
    max_persons = serializers.IntegerField(required=False)
    space_pks = serializers.ListField(source="spaces", required=False)
    resource_pks = serializers.ListField(source="resources", required=False)
    purpose_pks = serializers.ListField(source="purposes", required=False)
    equipment_pks = serializers.ListField(source="equipments", required=False)
    service_pks = serializers.ListField(source="services", required=False)
    reservation_unit_type_pk = serializers.PrimaryKeyRelatedField(
        source="reservation_unit_type",
        required=False,
        queryset=ReservationUnitType.objects.all(),
    )
    unit_pk = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(), source="unit"
    )

    translation_fields = get_all_translatable_fields(ReservationUnit)

    class Meta(ReservationUnitSerializer.Meta):
        fields = [
            "id",
            "spaces",
            "resources",
            "services",
            "require_introduction",
            "purposes",
            "images",
            "location",
            "max_persons",
            "reservation_unit_type",
            "building",
            "equipment_pks",
            "unit_pk",
            "uuid",
            "max_reservation_duration",
            "min_reservation_duration",
            "is_draft",
            "space_pks",
            "resource_pks",
            "purpose_pks",
            "service_pks",
            "reservation_unit_type_pk",
            "surface_area",
            "buffer_time_between_reservations",
        ] + get_all_translatable_fields(ReservationUnit)

    def _check_pk_list(self, id_list, field_name):
        for identifier in id_list:
            try:
                int(identifier)
            except ValueError:
                raise serializers.ValidationError(
                    f"Wrong type of id: {identifier} for {field_name}"
                )

    def validate(self, data):
        is_draft = data.get("is_draft", getattr(self.instance, "is_draft", False))

        if not is_draft:
            self.validate_for_publish(data)

        if "name_fi" in data.keys():
            name = data.get("name_fi")
            if not name or name.isspace():
                raise serializers.ValidationError(
                    "nameFi is required for draft reservation units."
                )

        return data

    def validate_space_pks(self, data):
        self._check_pk_list(data, "space_pks")
        spaces = Space.objects.filter(pk__in=data)
        return spaces

    def validate_resource_pks(self, data):
        self._check_pk_list(data, "resource_pks")
        resources = Resource.objects.filter(pk__in=data)
        return resources

    def validate_purpose_pks(self, data):
        self._check_pk_list(data, "purpose_pks")
        purposes = Purpose.objects.filter(pk__in=data)
        return purposes

    def validate_equipment_pks(self, data):
        self._check_pk_list(data, "equipment_pks")
        equipments = Equipment.objects.filter(pk__in=data)
        return equipments

    def validate_service_pks(self, data):
        self._check_pk_list(data, "service_pks")
        services = Service.objects.filter(pk__in=data)
        return services

    def validate_for_publish(self, data):
        """Validates necessary fields for published reservation unit."""
        for field in self.translation_fields:
            value = data.get(field, getattr(self.instance, field, None))
            if not value or value.isspace():
                raise serializers.ValidationError(
                    f"Not draft state reservation units must have a translations. Missing translation for {field}."
                )

        spaces = data.get("spaces", getattr(self.instance, "spaces", None))
        resources = data.get("resources", getattr(self.instance, "resources", None))
        if not (spaces or resources):
            raise serializers.ValidationError(
                "Not draft state reservation unit must have one or more space or resource defined"
            )

        reservation_unit_type = data.get(
            "reservation_unit_type",
            getattr(self.instance, "reservation_unit_type", None),
        )
        if not reservation_unit_type:
            raise serializers.ValidationError(
                "Not draft reservation unit must have a reservation unit type."
            )


class ReservationUnitUpdateSerializer(
    PrimaryKeyUpdateSerializer, ReservationUnitCreateSerializer
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unit_pk"].required = False

    class Meta(ReservationUnitCreateSerializer.Meta):
        fields = ReservationUnitCreateSerializer.Meta.fields + ["pk"]
