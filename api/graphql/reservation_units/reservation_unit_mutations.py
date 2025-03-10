import graphene
from django.conf import settings
from graphene import ClientIDMutation
from graphene_django.rest_framework.mutation import SerializerMutation
from graphene_django.types import ErrorType
from graphene_file_upload.scalars import Upload
from graphene_permissions.permissions import AllowAny
from rest_framework.generics import get_object_or_404

from api.graphql.base_mutations import AuthDeleteMutation, AuthSerializerMutation
from api.graphql.reservation_units.reservation_unit_serializers import (
    EquipmentCategoryCreateSerializer,
    EquipmentCategoryUpdateSerializer,
    EquipmentCreateSerializer,
    EquipmentUpdateSerializer,
    PurposeCreateSerializer,
    PurposeUpdateSerializer,
    ReservationUnitCreateSerializer,
    ReservationUnitImageCreateSerializer,
    ReservationUnitImageUpdateSerializer,
    ReservationUnitUpdateSerializer,
)
from api.graphql.reservation_units.reservation_unit_types import (
    EquipmentCategoryType,
    EquipmentType,
    PurposeType,
    ReservationUnitImageType,
    ReservationUnitType,
)
from opening_hours.errors import HaukiAPIError, HaukiRequestError
from permissions.api_permissions.graphene_permissions import (
    EquipmentCategoryPermission,
    EquipmentPermission,
    PurposePermission,
    ReservationUnitImagePermission,
    ReservationUnitPermission,
)
from reservation_units.models import (
    Equipment,
    EquipmentCategory,
    Purpose,
    ReservationUnitImage,
)
from reservation_units.utils.hauki_exporter import ReservationUnitHaukiExporter


class EquipmentCreateMutation(AuthSerializerMutation, SerializerMutation):
    equipment = graphene.Field(EquipmentType)

    permission_classes = (
        (EquipmentPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )

    class Meta:
        model_operations = ["create"]
        serializer_class = EquipmentCreateSerializer


class EquipmentUpdateMutation(AuthSerializerMutation, SerializerMutation):
    equipment = graphene.Field(EquipmentType)

    permission_classes = (
        (EquipmentPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )

    class Meta:
        model_operations = ["update"]
        lookup_field = "pk"
        serializer_class = EquipmentUpdateSerializer


class EquipmentDeleteMutation(AuthDeleteMutation, ClientIDMutation):
    permission_classes = (
        (EquipmentPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )
    model = Equipment

    @classmethod
    def validate(self, root, info, **input):
        return None


class EquipmentCategoryCreateMutation(AuthSerializerMutation, SerializerMutation):
    equipment_category = graphene.Field(EquipmentCategoryType)

    permission_classes = (
        (EquipmentCategoryPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model_operations = ["create"]
        serializer_class = EquipmentCategoryCreateSerializer


class EquipmentCategoryUpdateMutation(AuthSerializerMutation, SerializerMutation):
    equipment_category = graphene.Field(EquipmentCategoryType)

    permission_classes = (
        (EquipmentCategoryPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model_operations = ["update"]
        lookup_field = "pk"
        serializer_class = EquipmentCategoryUpdateSerializer


class EquipmentCategoryDeleteMutation(AuthDeleteMutation, ClientIDMutation):
    permission_classes = (
        (EquipmentCategoryPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )
    model = EquipmentCategory

    @classmethod
    def validate(self, root, info, **input):
        return None


class PurposeCreateMutation(AuthSerializerMutation, SerializerMutation):
    purpose = graphene.Field(PurposeType)

    permission_classes = (
        (PurposePermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )

    class Meta:
        model_operations = ["create"]

        serializer_class = PurposeCreateSerializer

    @classmethod
    def perform_mutate(cls, serializer, info):
        purpose = serializer.create(serializer.validated_data)
        return cls(errors=None, purpose=purpose)


class PurposeUpdateMutation(AuthSerializerMutation, SerializerMutation):
    purpose = graphene.Field(PurposeType)

    permission_classes = (
        (PurposePermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )

    class Meta:
        model_operations = ["update"]
        lookup_field = "pk"
        serializer_class = PurposeUpdateSerializer

    @classmethod
    def perform_mutate(cls, serializer, info):

        validated_data = serializer.validated_data
        pk = validated_data.get("pk")
        purpose = serializer.update(get_object_or_404(Purpose, pk=pk), validated_data)
        return cls(errors=None, purpose=purpose)


class ReservationUnitMutationMixin:
    @classmethod
    def perform_mutate(cls, serializer, info):
        """After serializer is validated and save we check if the reservation unit
        was published and thus should be sent to HAUKI and do it here."""

        mutation_response = super().perform_mutate(serializer, info)
        reservation_unit = serializer.instance
        if not settings.HAUKI_EXPORTS_ENABLED:
            return mutation_response

        exporter = ReservationUnitHaukiExporter(reservation_unit)
        try:
            exporter.send_reservation_unit_to_hauki()
        except (HaukiRequestError, HaukiAPIError):
            error = ErrorType(
                field="hauki_resource_id",
                messages=["Sending reservation unit as resource to HAUKI failed."],
            )
            mutation_response.errors = [error]

        return mutation_response


class ReservationUnitCreateMutation(
    ReservationUnitMutationMixin, AuthSerializerMutation, SerializerMutation
):
    reservation_unit = graphene.Field(ReservationUnitType)

    permission_classes = (
        (ReservationUnitPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model_operations = ["create"]

        serializer_class = ReservationUnitCreateSerializer


class ReservationUnitUpdateMutation(
    ReservationUnitMutationMixin, AuthSerializerMutation, SerializerMutation
):
    reservation_unit = graphene.Field(ReservationUnitType)

    permission_classes = (
        (ReservationUnitPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model_operations = ["update"]
        lookup_field = "pk"
        serializer_class = ReservationUnitUpdateSerializer


class ReservationUnitImageCreateMutation(AuthSerializerMutation, SerializerMutation):
    reservation_unit_image = graphene.Field(ReservationUnitImageType)

    class Input:
        image = Upload()

    permission_classes = (
        (ReservationUnitImagePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model_operations = ["create"]
        serializer_class = ReservationUnitImageCreateSerializer

    def resolve_reservation_unit_image(self, info):
        if self.pk:
            return get_object_or_404(ReservationUnitImage, pk=self.pk)
        return None


class ReservationUnitImageUpdateMutation(AuthSerializerMutation, SerializerMutation):
    reservation_unit_image = graphene.Field(ReservationUnitImageType)

    permission_classes = (
        (ReservationUnitImagePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model_operations = ["update"]
        lookup_field = "pk"
        serializer_class = ReservationUnitImageUpdateSerializer


class ReservationUnitImageDeleteMutation(AuthDeleteMutation, ClientIDMutation):
    permission_classes = (
        (ReservationUnitImagePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )
    model = ReservationUnitImage

    @classmethod
    def validate(self, root, info, **input):
        return None
