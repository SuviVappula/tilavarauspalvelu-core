import django_filters
import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from graphene import Field, relay
from graphene_permissions.mixins import AuthFilter
from graphene_permissions.permissions import AllowAny, AllowAuthenticated
from rest_framework.generics import get_object_or_404

from api.graphql.applications.application_types import CityType
from api.graphql.reservation_units.reservation_unit_filtersets import (
    ReservationUnitsFilterSet,
)
from api.graphql.reservation_units.reservation_unit_mutations import (
    EquipmentCategoryCreateMutation,
    EquipmentCategoryDeleteMutation,
    EquipmentCategoryUpdateMutation,
    EquipmentCreateMutation,
    EquipmentDeleteMutation,
    EquipmentUpdateMutation,
    PurposeCreateMutation,
    PurposeUpdateMutation,
    ReservationUnitCreateMutation,
    ReservationUnitImageCreateMutation,
    ReservationUnitImageDeleteMutation,
    ReservationUnitImageUpdateMutation,
    ReservationUnitUpdateMutation,
)
from api.graphql.reservation_units.reservation_unit_types import (
    EquipmentCategoryType,
    EquipmentType,
    KeywordCategoryType,
    KeywordGroupType,
    KeywordType,
    PurposeType,
    ReservationUnitByPkType,
    ReservationUnitCancellationRuleType,
    ReservationUnitType,
    ReservationUnitTypeType,
    TaxPercentageType,
)
from api.graphql.reservations.reservation_filtersets import ReservationFilterSet
from api.graphql.reservations.reservation_mutations import (
    ReservationApproveMutation,
    ReservationCancellationMutation,
    ReservationConfirmMutation,
    ReservationCreateMutation,
    ReservationDenyMutation,
    ReservationRequiresHandlingMutation,
    ReservationUpdateMutation,
    ReservationWorkingMemoMutation,
)
from api.graphql.reservations.reservation_types import (
    AgeGroupType,
    ReservationCancelReasonType,
    ReservationDenyReasonType,
    ReservationMetadataSetType,
    ReservationPurposeType,
    ReservationType,
)
from api.graphql.resources.resource_mutations import (
    ResourceCreateMutation,
    ResourceDeleteMutation,
    ResourceUpdateMutation,
)
from api.graphql.resources.resource_types import ResourceType
from api.graphql.spaces.space_mutations import (
    SpaceCreateMutation,
    SpaceDeleteMutation,
    SpaceUpdateMutation,
)
from api.graphql.spaces.space_types import SpaceType
from api.graphql.terms_of_use.terms_of_use_types import TermsOfUseType
from api.graphql.units.unit_mutations import UnitUpdateMutation
from api.graphql.units.unit_types import UnitByPkType, UnitType
from permissions.api_permissions.graphene_field_decorators import (
    check_resolver_permission,
)
from permissions.api_permissions.graphene_permissions import (
    AgeGroupPermission,
    CityPermission,
    EquipmentCategoryPermission,
    EquipmentPermission,
    KeywordPermission,
    PurposePermission,
    ReservationMetadataSetPermission,
    ReservationPermission,
    ReservationPurposePermission,
    ReservationUnitCancellationRulePermission,
    ReservationUnitPermission,
    ResourcePermission,
    SpacePermission,
    TaxPercentagePermission,
    TermsOfUsePermission,
    UnitPermission,
)
from permissions.helpers import (
    get_service_sectors_where_can_view_reservations,
    get_units_where_can_view_reservations,
)
from reservation_units.models import Equipment, EquipmentCategory, ReservationUnit
from reservations.models import Reservation
from resources.models import Resource
from spaces.models import ServiceSector, Space, Unit


class AllowAuthenticatedFilter(AuthFilter):
    permission_classes = (AllowAuthenticated,)


class ReservationsFilter(AuthFilter, django_filters.FilterSet):
    permission_classes = (
        (ReservationPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        queryset = super().resolve_queryset(
            connection, iterable, info, args, filtering_args, filterset_class
        )

        user = info.context.user
        viewable_units = get_units_where_can_view_reservations(user)
        viewable_service_sectors = get_service_sectors_where_can_view_reservations(user)
        if settings.TMP_PERMISSIONS_DISABLED:
            viewable_units = Unit.objects.all()
            viewable_service_sectors = ServiceSector.objects.all()
            user = (
                get_user_model().objects.get(username="admin")
                if settings.TMP_PERMISSIONS_DISABLED
                else info.context.user
            )
        elif user.is_anonymous:
            return queryset.none()
        qs = queryset.filter(
            Q(reservation_unit__unit__in=viewable_units)
            | Q(reservation_unit__unit__service_sectors__in=viewable_service_sectors)
            | Q(user=user)
        ).distinct()
        if not args.get("order_by", None):
            qs = qs.order_by("begin")
        return qs


class ReservationUnitsFilter(AuthFilter, django_filters.FilterSet):
    permission_classes = (
        (ReservationUnitPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class ReservationUnitTypesFilter(AuthFilter, django_filters.FilterSet):
    permission_classes = (
        (ReservationUnitPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class ResourcesFilter(AuthFilter):
    permission_classes = (
        (ResourcePermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class SpacesFilter(AuthFilter):
    permission_classes = (
        (SpacePermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class UnitsFilter(AuthFilter):
    permission_classes = (
        (UnitPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class KeywordFilter(AuthFilter):
    permission_classes = (
        (KeywordPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class EquipmentFilter(AuthFilter):
    permission_classes = (
        (EquipmentPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class EquipmentCategoryFilter(AuthFilter):
    permission_classes = (
        (EquipmentCategoryPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class PurposeFilter(AuthFilter):
    permission_classes = (
        (PurposePermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class ReservationPurposeFilter(AuthFilter):
    permission_classes = (
        (ReservationPurposePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class ReservationCancelReasonFilter(AuthFilter):
    permission_classes = (
        (AllowAuthenticated,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class ReservationDenyReasonFilter(AuthFilter):
    permission_classes = (
        (AllowAuthenticated,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class ReservationUnitCancellationRulesFilter(AuthFilter):
    permission_classes = (
        (ReservationUnitCancellationRulePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class TermsOfUseFilter(AuthFilter):
    permission_classes = (
        (TermsOfUsePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class TaxPercentageFilter(AuthFilter):
    permission_classes = (
        (TaxPercentagePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class AgeGroupFilter(AuthFilter):
    permission_classes = (
        (AgeGroupPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class CityFilter(AuthFilter):
    permission_classes = (
        (CityPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )


class ReservationMetadataSetFilter(AuthFilter):
    permission_classes = (
        (ReservationMetadataSetPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )


class Query(graphene.ObjectType):
    reservations = ReservationsFilter(
        ReservationType, filterset_class=ReservationFilterSet
    )
    reservation_by_pk = Field(ReservationType, pk=graphene.Int())

    reservation_cancel_reasons = ReservationCancelReasonFilter(
        ReservationCancelReasonType
    )

    reservation_deny_reasons = ReservationDenyReasonFilter(ReservationDenyReasonType)

    reservation_units = ReservationUnitsFilter(
        ReservationUnitType, filterset_class=ReservationUnitsFilterSet
    )
    reservation_unit = relay.Node.Field(ReservationUnitType)
    reservation_unit_by_pk = Field(ReservationUnitByPkType, pk=graphene.Int())
    reservation_unit_cancellation_rules = ReservationUnitCancellationRulesFilter(
        ReservationUnitCancellationRuleType
    )

    reservation_unit_types = ReservationUnitTypesFilter(ReservationUnitTypeType)

    resources = ResourcesFilter(ResourceType)
    resource = relay.Node.Field(ResourceType)
    resource_by_pk = Field(ResourceType, pk=graphene.Int())

    equipments = EquipmentFilter(EquipmentType)
    equipment = relay.Node.Field((EquipmentType))
    equipment_by_pk = Field(EquipmentType, pk=graphene.Int())

    equipment_categories = EquipmentCategoryFilter(EquipmentCategoryType)
    equipment_category = relay.Node.Field((EquipmentCategoryType))
    equipment_category_by_pk = Field(EquipmentCategoryType, pk=graphene.Int())

    spaces = SpacesFilter(SpaceType)
    space = relay.Node.Field(SpaceType)
    space_by_pk = Field(SpaceType, pk=graphene.Int())

    units = UnitsFilter(UnitType)
    unit = relay.Node.Field(UnitType)
    unit_by_pk = Field(UnitByPkType, pk=graphene.Int())

    keyword_categories = KeywordFilter(KeywordCategoryType)
    keyword_groups = KeywordFilter(KeywordGroupType)
    keywords = KeywordFilter(KeywordType)

    purposes = PurposeFilter(PurposeType)
    reservation_purposes = ReservationPurposeFilter(ReservationPurposeType)

    terms_of_use = TermsOfUseFilter(TermsOfUseType)
    tax_percentages = TaxPercentageFilter(TaxPercentageType)
    age_groups = AgeGroupFilter(AgeGroupType)
    cities = CityFilter(CityType)
    metadata_sets = ReservationMetadataSetFilter(ReservationMetadataSetType)

    @check_resolver_permission(ReservationPermission)
    def resolve_reservation_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(Reservation, pk=pk)

    @check_resolver_permission(ReservationUnitPermission)
    def resolve_reservation_unit_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(ReservationUnit, pk=pk)

    @check_resolver_permission(ResourcePermission)
    def resolve_resource_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(Resource, pk=pk)

    @check_resolver_permission(UnitPermission)
    def resolve_unit_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(Unit, pk=pk)

    @check_resolver_permission(SpacePermission)
    def resolve_space_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(Space, pk=pk)

    @check_resolver_permission(EquipmentPermission)
    def resolve_equipment_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(Equipment, pk=pk)

    @check_resolver_permission(EquipmentCategoryPermission)
    def resolve_equipment_category_by_pk(self, info, **kwargs):
        pk = kwargs.get("pk")
        return get_object_or_404(EquipmentCategory, pk=pk)


class Mutation(graphene.ObjectType):
    create_reservation = ReservationCreateMutation.Field()
    update_reservation = ReservationUpdateMutation.Field()
    confirm_reservation = ReservationConfirmMutation.Field()
    cancel_reservation = ReservationCancellationMutation.Field()
    deny_reservation = ReservationDenyMutation.Field()
    approve_reservation = ReservationApproveMutation.Field()
    require_handling_for_reservation = ReservationRequiresHandlingMutation.Field()
    update_reservation_working_memo = ReservationWorkingMemoMutation.Field()

    create_reservation_unit = ReservationUnitCreateMutation.Field()
    update_reservation_unit = ReservationUnitUpdateMutation.Field()

    create_reservation_unit_image = ReservationUnitImageCreateMutation.Field()
    update_reservation_unit_image = ReservationUnitImageUpdateMutation.Field()
    delete_reservation_unit_image = ReservationUnitImageDeleteMutation.Field()

    create_purpose = PurposeCreateMutation.Field()
    update_purpose = PurposeUpdateMutation.Field()

    create_equipment = EquipmentCreateMutation.Field()
    update_equipment = EquipmentUpdateMutation.Field()
    delete_equipment = EquipmentDeleteMutation.Field()

    create_equipment_category = EquipmentCategoryCreateMutation.Field()
    update_equipment_category = EquipmentCategoryUpdateMutation.Field()
    delete_equipment_category = EquipmentCategoryDeleteMutation.Field()

    create_space = SpaceCreateMutation.Field()
    update_space = SpaceUpdateMutation.Field()
    delete_space = SpaceDeleteMutation.Field()

    create_resource = ResourceCreateMutation.Field()
    update_resource = ResourceUpdateMutation.Field()
    delete_resource = ResourceDeleteMutation.Field()

    update_unit = UnitUpdateMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
