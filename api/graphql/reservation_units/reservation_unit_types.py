import datetime
from typing import List, Optional

import graphene
from django.conf import settings
from django.db.models import Q, QuerySet, Sum
from easy_thumbnails.files import get_thumbnailer
from graphene import ResolveInfo
from graphene_django import DjangoObjectType
from graphene_permissions.mixins import AuthNode
from graphene_permissions.permissions import AllowAny

from api.graphql.base_type import PrimaryKeyObjectType
from api.graphql.duration_field import Duration
from api.graphql.opening_hours.opening_hours_types import OpeningHoursMixin
from api.graphql.reservations.reservation_types import (
    ReservationMetadataSetType,
    ReservationType,
)
from api.graphql.resources.resource_types import ResourceType
from api.graphql.services.service_types import ServiceType
from api.graphql.spaces.space_types import LocationType, SpaceType
from api.graphql.terms_of_use.terms_of_use_types import TermsOfUseType
from api.graphql.translate_fields import get_all_translatable_fields
from api.graphql.units.unit_types import UnitType
from applications.models import ApplicationRound
from opening_hours.hauki_link_generator import generate_hauki_link
from permissions.api_permissions.drf_permissions import ApplicationRoundPermission
from permissions.api_permissions.graphene_field_decorators import (
    check_resolver_permission,
)
from permissions.api_permissions.graphene_permissions import (
    EquipmentCategoryPermission,
    EquipmentPermission,
    PurposePermission,
    ReservationPermission,
    ReservationUnitCancellationRulePermission,
    ReservationUnitHaukiUrlPermission,
    ReservationUnitPermission,
    ResourcePermission,
    ServicePermission,
    SpacePermission,
    UnitPermission,
)
from permissions.helpers import can_manage_units
from reservation_units.models import (
    Equipment,
    EquipmentCategory,
    Keyword,
    KeywordCategory,
    KeywordGroup,
    Purpose,
    ReservationUnit,
    ReservationUnitCancellationRule,
    ReservationUnitImage,
)
from reservation_units.models import ReservationUnitType as ReservationUnitTypeModel
from reservation_units.models import TaxPercentage
from reservation_units.utils.reservation_unit_reservation_scheduler import (
    ReservationUnitReservationScheduler,
)
from resources.models import Resource
from spaces.models import Space


class KeywordType(AuthNode, PrimaryKeyObjectType):
    class Meta:
        model = Keyword
        fields = ["pk"] + get_all_translatable_fields(model)
        filter_fields = ["name_fi", "name_sv", "name_en"]
        interfaces = (graphene.relay.Node,)


class TaxPercentageType(AuthNode, PrimaryKeyObjectType):
    class Meta:
        model = TaxPercentage
        fields = ["pk", "value"]
        filter_fields = ["value"]
        interfaces = (graphene.relay.Node,)


class KeywordGroupType(AuthNode, PrimaryKeyObjectType):

    keywords = graphene.List(KeywordType)

    class Meta:
        model = KeywordGroup
        fields = ["pk"] + get_all_translatable_fields(model)
        filter_fields = ["name_fi", "name_sv", "name_en"]
        interfaces = (graphene.relay.Node,)

    def resolve_keywords(self, info):
        return self.keywords.all()


class KeywordCategoryType(AuthNode, PrimaryKeyObjectType):
    keyword_groups = graphene.List(KeywordGroupType)

    class Meta:
        model = KeywordCategory
        fields = ["pk"] + get_all_translatable_fields(model)
        filter_fields = ["name_fi", "name_sv", "name_en"]
        interfaces = (graphene.relay.Node,)

    def resolve_keyword_groups(self, info):
        return self.keyword_groups.all()


class PurposeType(AuthNode, PrimaryKeyObjectType):
    permission_classes = (
        (PurposePermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )

    class Meta:
        model = Purpose
        fields = ["pk"] + get_all_translatable_fields(model)
        filter_fields = ["name_fi", "name_en", "name_sv"]
        interfaces = (graphene.relay.Node,)


class ReservationUnitHaukiUrlType(AuthNode, DjangoObjectType):

    url = graphene.String()

    permission_classes = (
        (ReservationUnitHaukiUrlPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model = ReservationUnit
        fields = ("url",)

    def resolve_url(self, info):
        if settings.TMP_PERMISSIONS_DISABLED or can_manage_units(
            info.context.user, self.unit
        ):
            return generate_hauki_link(
                self.uuid,
                getattr(info.context.user, "email", ""),
                self.unit.tprek_department_id,
            )
        return None


class ReservationUnitImageType(PrimaryKeyObjectType):
    image_url = graphene.String()
    medium_url = graphene.String()
    small_url = graphene.String()

    class Meta:
        model = ReservationUnitImage
        fields = ["pk", "image_url", "medium_url", "small_url", "image_type"]

    def resolve_image_url(self, info):
        if not self.image:
            return None
        return info.context.build_absolute_uri(self.image.url)

    def resolve_small_url(self, info):
        if not self.image:
            return None
        url = get_thumbnailer(self.image)["small"].url

        return info.context.build_absolute_uri(url)

    def resolve_medium_url(self, info):
        if not self.image:
            return None
        url = get_thumbnailer(self.image)["medium"].url

        return info.context.build_absolute_uri(url)


class ReservationUnitCancellationRuleType(AuthNode, PrimaryKeyObjectType):
    permission_classes = (
        (ReservationUnitCancellationRulePermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model = ReservationUnitCancellationRule
        fields = [
            "pk",
            "can_be_cancelled_time_before",
            "needs_handling",
        ] + get_all_translatable_fields(model)
        filter_fields = ["name"]
        interfaces = (graphene.relay.Node,)

    def resolve_can_be_cancelled_time_before(self, info: ResolveInfo):
        if not self.can_be_cancelled_time_before:
            return None
        return self.can_be_cancelled_time_before.total_seconds()


class ReservationUnitTypeType(PrimaryKeyObjectType):
    class Meta:
        model = ReservationUnitTypeModel
        fields = ["pk"] + get_all_translatable_fields(model)
        filter_fields = get_all_translatable_fields(model)

        interfaces = (graphene.relay.Node,)


class EquipmentCategoryType(AuthNode, PrimaryKeyObjectType):
    permission_classes = (
        (EquipmentCategoryPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model = EquipmentCategory
        fields = ["pk"] + get_all_translatable_fields(model)

        filter_fields = {
            "name_fi": ["exact", "icontains", "istartswith"],
            "name_sv": ["exact", "icontains", "istartswith"],
            "name_en": ["exact", "icontains", "istartswith"],
        }

        interfaces = (graphene.relay.Node,)


class EquipmentType(AuthNode, PrimaryKeyObjectType):
    permission_classes = (
        (EquipmentPermission,) if not settings.TMP_PERMISSIONS_DISABLED else (AllowAny,)
    )
    category = graphene.Field(EquipmentCategoryType)

    class Meta:
        model = Equipment
        fields = ["pk"] + get_all_translatable_fields(model)

        filter_fields = {
            "name_fi": ["exact", "icontains", "istartswith"],
            "name_sv": ["exact", "icontains", "istartswith"],
            "name_en": ["exact", "icontains", "istartswith"],
        }

        interfaces = (graphene.relay.Node,)

    def resolve_category(self, info):
        return self.category


class ApplicationRoundType(AuthNode, PrimaryKeyObjectType):
    permission_classes = (
        (ApplicationRoundPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Input:
        active = graphene.Field(graphene.Boolean)

    class Meta:
        model = ApplicationRound
        fields = [
            "target_group",
            "allocating",
            "reservation_units",
            "application_period_begin",
            "application_period_end",
            "reservation_period_begin",
            "reservation_period_end",
            "public_display_begin",
            "public_display_end",
            "purposes",
            "service_sector",
        ] + get_all_translatable_fields(model)

        filter_fields = {
            "name_fi": ["exact", "icontains", "istartswith"],
            "name_sv": ["exact", "icontains", "istartswith"],
            "name_en": ["exact", "icontains", "istartswith"],
        }


class ReservationUnitType(AuthNode, PrimaryKeyObjectType):
    name_fi = graphene.String()
    name_sv = graphene.String()
    name_en = graphene.String()
    spaces = graphene.List(SpaceType)
    resources = graphene.List(ResourceType)
    services = graphene.List(ServiceType)
    purposes = graphene.List(PurposeType)
    images = graphene.List(ReservationUnitImageType)
    location = graphene.Field(LocationType)
    reservation_unit_type = graphene.Field(ReservationUnitTypeType)
    equipment = graphene.List(EquipmentType)
    unit = graphene.Field(UnitType)
    max_persons = graphene.Int()
    surface_area = graphene.Decimal()
    max_reservation_duration = Duration()
    min_reservation_duration = Duration()
    keyword_groups = graphene.List(KeywordGroupType)
    reservations = graphene.List(
        ReservationType,
        from_=graphene.Date(name="from"),
        to=graphene.Date(),
        state=graphene.List(graphene.String),
    )
    application_rounds = graphene.List(ApplicationRoundType, active=graphene.Boolean())
    cancellation_rule = graphene.Field(ReservationUnitCancellationRuleType)
    payment_terms = graphene.Field(TermsOfUseType)
    cancellation_terms = graphene.Field(TermsOfUseType)
    service_specific_terms = graphene.Field(TermsOfUseType)
    tax_percentage = graphene.Field(TaxPercentageType)
    buffer_time_before = Duration()
    buffer_time_after = Duration()
    metadata_set = graphene.Field(ReservationMetadataSetType)

    permission_classes = (
        (ReservationUnitPermission,)
        if not settings.TMP_PERMISSIONS_DISABLED
        else (AllowAny,)
    )

    class Meta:
        model = ReservationUnit
        fields = [
            "spaces",
            "resources",
            "services",
            "require_introduction",
            "purposes",
            "images",
            "location",
            "max_persons",
            "reservation_unit_type",
            "equipment",
            "uuid",
            "max_reservation_duration",
            "min_reservation_duration",
            "is_draft",
            "surface_area",
            "buffer_time_before",
            "buffer_time_after",
            "reservations",
            "application_rounds",
            "cancellation_rule",
            "payment_terms",
            "cancellation_terms",
            "service_specific_terms",
            "tax_percentage",
            "lowest_price",
            "highest_price",
            "price_unit",
            "reservation_start_interval",
            "reservation_begins",
            "reservation_ends",
            "publish_begins",
            "publish_ends",
            "metadata_set",
            "max_reservations_per_user",
            "require_reservation_handling",
        ] + get_all_translatable_fields(model)
        filter_fields = {
            "name_fi": ["exact", "icontains", "istartswith"],
            "name_sv": ["exact", "icontains", "istartswith"],
            "name_en": ["exact", "icontains", "istartswith"],
            "description_fi": ["exact", "icontains"],
            "description_sv": ["exact", "icontains"],
            "description_en": ["exact", "icontains"],
        }

        interfaces = (graphene.relay.Node,)

    def resolve_pk(self, info):
        return self.id

    def resolve_location(self, info):
        return self.get_location()

    @check_resolver_permission(SpacePermission)
    def resolve_spaces(self, info):
        return Space.objects.filter(reservation_units=self.id).select_related(
            "parent", "building"
        )

    @check_resolver_permission(ServicePermission)
    def resolve_services(self, info):
        return self.services.all()

    @check_resolver_permission(PurposePermission)
    def resolve_purposes(self, info):
        return Purpose.objects.filter(reservation_units=self.id)

    def resolve_images(self, info):
        return ReservationUnitImage.objects.filter(reservation_unit_id=self.id)

    @check_resolver_permission(ResourcePermission)
    def resolve_resources(self, info):
        return Resource.objects.filter(reservation_units=self.id)

    def resolve_reservation_unit_type(self, info):
        return self.reservation_unit_type

    @check_resolver_permission(EquipmentPermission)
    def resolve_equipment(self, info):
        if self.equipments is None:
            return []
        return self.equipments.all()

    @check_resolver_permission(UnitPermission)
    def resolve_unit(self, info):
        return self.unit

    def resolve_max_persons(self, info):
        if not self.max_persons:
            # Gets the max persons from spaces.
            return self.get_max_persons()
        return self.max_persons

    def resolve_surface_area(self, info):
        if self.surface_area is not None:
            return self.surface_area
        surface_area = self.spaces.aggregate(total_surface_area=Sum("surface_area"))
        return surface_area.get("total_surface_area")

    def resolve_keyword_groups(self, info):
        return KeywordGroup.objects.filter(reservation_units=self.id)

    @check_resolver_permission(ReservationPermission)
    def resolve_reservations(
        self,
        info: ResolveInfo,
        from_: Optional[datetime.date] = None,
        to: Optional[datetime.date] = None,
        state: Optional[List[str]] = None,
    ) -> QuerySet:
        reservations = self.reservation_set.all()
        if from_ is not None:
            reservations = reservations.filter(begin__gte=from_)
        if to is not None:
            reservations = reservations.filter(end__lte=to)
        if state is not None:
            reservations = reservations.filter(state__in=state)
        return reservations

    def resolve_application_rounds(
        self, info: ResolveInfo, active: Optional[bool] = None
    ) -> QuerySet:
        application_rounds = self.application_rounds.all()
        if active is None:
            return application_rounds
        now = datetime.datetime.now().astimezone()
        active_filter = Q(
            application_period_begin__lte=now,
            application_period_end__gte=now,
        )
        return application_rounds.filter(active_filter if active else ~active_filter)

    @check_resolver_permission(ReservationUnitCancellationRulePermission)
    def resolve_cancellation_rule(self, info: ResolveInfo):
        return self.cancellation_rule


class ReservationUnitByPkType(ReservationUnitType, OpeningHoursMixin):
    next_available_slot = graphene.DateTime()

    hauki_url = graphene.Field(ReservationUnitHaukiUrlType)

    class Meta:
        model = ReservationUnit
        fields = [
            "pk",
            "spaces",
            "resources",
            "services",
            "require_introduction",
            "purposes",
            "images",
            "location",
            "max_persons",
            "reservation_unit_type",
            "equipment",
            "uuid",
            "max_reservation_duration",
            "min_reservation_duration",
            "next_available_slot",
            "hauki_url",
            "is_draft",
            "tax_percentage",
            "lowest_price",
            "highest_price",
            "price_unit",
            "reservation_start_interval",
            "buffer_time_before",
            "buffer_time_after",
            "metadata_set",
            "reservation_begins",
            "reservation_ends",
            "publish_begins",
            "publish_ends",
            "max_reservations_per_user",
            "require_reservation_handling",
        ] + get_all_translatable_fields(model)

        interfaces = (graphene.relay.Node,)

    def resolve_next_available_slot(self, info):
        scheduler = ReservationUnitReservationScheduler(self)
        start, end = scheduler.get_next_available_reservation_time()
        return start

    def resolve_hauki_url(self, info):
        return self
