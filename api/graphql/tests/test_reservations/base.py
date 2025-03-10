import datetime
from typing import Optional

import freezegun
import snapshottest
from django.conf import settings
from django.utils.timezone import get_default_timezone

from api.graphql.tests.base import GrapheneTestCaseBase
from opening_hours.enums import State
from opening_hours.hours import TimeElement
from reservation_units.models import ReservationUnit
from reservation_units.tests.factories import ReservationUnitFactory
from reservations.models import ReservationMetadataField, ReservationMetadataSet
from reservations.tests.factories import ReservationPurposeFactory
from spaces.tests.factories import SpaceFactory

DEFAULT_TIMEZONE = get_default_timezone()


@freezegun.freeze_time("2021-10-12T12:00:00Z")
class ReservationTestCaseBase(GrapheneTestCaseBase, snapshottest.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.space = SpaceFactory()
        cls.reservation_unit = ReservationUnitFactory(
            spaces=[cls.space],
            name="resunit",
            reservation_start_interval=ReservationUnit.RESERVATION_START_INTERVAL_15_MINUTES,
        )
        cls.purpose = ReservationPurposeFactory(name="purpose")

    def get_mocked_opening_hours(
        self, reservation_unit: Optional[ReservationUnit] = None
    ):
        if reservation_unit is None:
            reservation_unit = self.reservation_unit
        resource_id = f"{settings.HAUKI_ORIGIN_ID}:{reservation_unit.uuid}"
        origin_id = str(reservation_unit.uuid)
        return [self._get_single_opening_hour_block(resource_id, origin_id)]

    def _get_single_opening_hour_block(self, resource_id, origin_id):
        return {
            "timezone": DEFAULT_TIMEZONE,
            "resource_id": resource_id,
            "origin_id": origin_id,
            "date": datetime.date.today(),
            "times": [
                TimeElement(
                    start_time=datetime.time(hour=6),
                    end_time=datetime.time(hour=22),
                    end_time_on_next_day=False,
                    resource_state=State.WITH_RESERVATION,
                    periods=[],
                ),
            ],
        }

    def _create_metadata_set(self):
        supported_fields = ReservationMetadataField.objects.filter(
            field_name__in=[
                "reservee_first_name",
                "reservee_last_name",
                "reservee_phone",
                "home_city",
                "age_group",
            ]
        )
        required_fields = ReservationMetadataField.objects.filter(
            field_name__in=[
                "reservee_first_name",
                "reservee_last_name",
                "home_city",
                "age_group",
            ]
        )
        metadata_set = ReservationMetadataSet.objects.create(name="Test form")
        metadata_set.supported_fields.set(supported_fields)
        metadata_set.required_fields.set(required_fields)
        return metadata_set
