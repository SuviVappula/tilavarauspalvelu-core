import datetime
import json

import freezegun
from assertpy import assert_that
from django.utils.timezone import get_default_timezone

from api.graphql.tests.test_reservations.base import ReservationTestCaseBase
from reservations.models import STATE_CHOICES
from reservations.tests.factories import (
    ReservationDenyReasonFactory,
    ReservationFactory,
    ReservationMetadataSetFactory,
)


@freezegun.freeze_time("2021-10-12T12:00:00Z")
class ReservationDenyTestCase(ReservationTestCaseBase):
    def setUp(self):
        super().setUp()
        metadata = ReservationMetadataSetFactory()
        self.reservation_unit.metadata_set = metadata
        self.reservation_unit.save()
        self.reservation = ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=datetime.datetime.now(tz=get_default_timezone())
            + datetime.timedelta(hours=1),
            end=(
                datetime.datetime.now(tz=get_default_timezone())
                + datetime.timedelta(hours=2)
            ),
            state=STATE_CHOICES.REQUIRES_HANDLING,
            user=self.regular_joe,
        )
        self.reason = ReservationDenyReasonFactory(
            reason_fi="syy", reason_en="reason", reason_sv="resonera"
        )

    def get_handle_query(self):
        return """
            mutation denyReservation($input: ReservationDenyMutationInput!) {
                denyReservation(input: $input) {
                    state
                    errors {
                        field
                        messages
                    }
                }
            }
        """

    def get_valid_deny_data(self):
        return {
            "pk": self.reservation.pk,
            "handlingDetails": "no can do",
            "denyReasonPk": self.reason.pk,
        }

    def test_deny_success_when_admin(self):
        self.client.force_login(self.general_admin)
        input_data = self.get_valid_deny_data()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.REQUIRES_HANDLING)
        response = self.query(self.get_handle_query(), input_data=input_data)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        deny_data = content.get("data").get("denyReservation")
        assert_that(deny_data.get("errors")).is_none()
        assert_that(deny_data.get("state")).is_equal_to(STATE_CHOICES.DENIED.upper())
        self.reservation.refresh_from_db()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.DENIED)
        assert_that(self.reservation.handling_details).is_equal_to("no can do")
        assert_that(self.reservation.handled_at).is_not_none()

    def test_cant_deny_if_regular_user(self):
        self.client.force_login(self.regular_joe)
        input_data = self.get_valid_deny_data()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.REQUIRES_HANDLING)
        response = self.query(self.get_handle_query(), input_data=input_data)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()
        deny_data = content.get("data").get("denyReservation")
        assert_that(deny_data).is_none()
        self.reservation.refresh_from_db()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.REQUIRES_HANDLING)

    def test_cant_deny_if_status_not_requires_handling(self):
        self.client.force_login(self.general_admin)
        input_data = self.get_valid_deny_data()
        self.reservation.state = STATE_CHOICES.CREATED
        self.reservation.save()
        response = self.query(self.get_handle_query(), input_data=input_data)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        handle_data = content.get("data").get("denyReservation")
        assert_that(handle_data.get("errors")).is_not_none()
        self.reservation.refresh_from_db()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.CREATED)
        assert_that(self.reservation.handling_details).is_empty()

    def test_denying_fails_when_reason_missing(self):
        self.client.force_login(self.general_admin)
        input_data = self.get_valid_deny_data()
        input_data.pop("denyReasonPk")
        response = self.query(self.get_handle_query(), input_data=input_data)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()
        self.reservation.refresh_from_db()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.REQUIRES_HANDLING)
        assert_that(self.reservation.handling_details).is_empty()

    def test_handling_details_saves_to_working_memo_also(self):
        self.client.force_login(self.general_admin)
        input_data = self.get_valid_deny_data()
        response = self.query(self.get_handle_query(), input_data=input_data)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.reservation.refresh_from_db()
        assert_that(self.reservation.state).is_equal_to(STATE_CHOICES.DENIED)
        assert_that(self.reservation.handling_details).is_equal_to(
            self.reservation.working_memo
        )
