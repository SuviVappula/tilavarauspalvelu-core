import datetime
import json
from unittest.mock import patch

import freezegun
from assertpy import assert_that

from api.graphql.tests.test_reservations.base import (
    DEFAULT_TIMEZONE,
    ReservationTestCaseBase,
)
from applications.models import PRIORITY_CONST, City
from applications.tests.factories import ApplicationRoundFactory
from opening_hours.tests.test_get_periods import get_mocked_periods
from reservation_units.models import ReservationUnit
from reservation_units.tests.factories import ReservationUnitFactory
from reservations.models import STATE_CHOICES, AgeGroup, Reservation
from reservations.tests.factories import ReservationFactory


@freezegun.freeze_time("2021-10-12T12:00:00Z")
@patch("opening_hours.utils.opening_hours_client.get_opening_hours")
@patch(
    "opening_hours.hours.get_periods_for_resource", return_value=get_mocked_periods()
)
class ReservationCreateTestCase(ReservationTestCaseBase):
    def get_create_query(self):
        return """
            mutation createReservation($input: ReservationCreateMutationInput!) {
                createReservation(input: $input) {
                    reservation {
                        pk
                        priority
                        calendarUrl
                    }
                    errors {
                        field
                        messages
                    }
                }
            }
        """

    def get_valid_input_data(self):
        return {
            "reserveeType": "individual",
            "reserveeFirstName": "John",
            "reserveeLastName": "Doe",
            "reserveeOrganisationName": "Test Organisation ry",
            "reserveePhone": "+358123456789",
            "reserveeEmail": "john.doe@example.com",
            "reserveeId": "2882333-2",
            "reserveeIsUnregisteredAssociation": False,
            "reserveeAddressStreet": "Mannerheimintie 2",
            "reserveeAddressCity": "Helsinki",
            "reserveeAddressZip": "00100",
            "billingFirstName": "Jane",
            "billingLastName": "Doe",
            "billingPhone": "+358234567890",
            "billingEmail": "jane.doe@example.com",
            "billingAddressStreet": "Auratie 12B",
            "billingAddressCity": "Turku",
            "billingAddressZip": "20100",
            "homeCityPk": City.objects.create(name="Helsinki").pk,
            "ageGroupPk": AgeGroup.objects.create(minimum=18, maximum=30).pk,
            "applyingForFreeOfCharge": True,
            "freeOfChargeReason": "Some reason here.",
            "name": "Test reservation",
            "description": "Test description",
            "numPersons": 1,
            "purposePk": self.purpose.pk,
            "begin": datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ"),
            "end": (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(
                "%Y%m%dT%H%M%SZ"
            ),
            "reservationUnitPks": [self.reservation_unit.pk],
        }

    def setUp(self):
        super().setUp()
        self.reservation_unit = ReservationUnitFactory(
            spaces=[self.space],
            name="resunit",
            reservation_start_interval=ReservationUnit.RESERVATION_START_INTERVAL_15_MINUTES,
            buffer_time_before=datetime.timedelta(minutes=30),
            buffer_time_after=datetime.timedelta(minutes=30),
        )

    def test_creating_reservation_succeed(self, mock_periods, mock_opening_hours):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        input_data = self.get_valid_input_data()
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("reservation").get("pk")
        ).is_not_none()
        pk = content.get("data").get("createReservation").get("reservation").get("pk")
        reservation = Reservation.objects.get(id=pk)
        assert_that(reservation).is_not_none()
        assert_that(reservation.user).is_equal_to(self.regular_joe)
        assert_that(reservation.state).is_equal_to(STATE_CHOICES.CREATED)
        assert_that(reservation.priority).is_equal_to(PRIORITY_CONST.PRIORITY_MEDIUM)
        assert_that(reservation.reservee_first_name).is_equal_to(
            input_data["reserveeFirstName"]
        )
        assert_that(reservation.reservee_last_name).is_equal_to(
            input_data["reserveeLastName"]
        )
        assert_that(reservation.reservee_phone).is_equal_to(input_data["reserveePhone"])
        assert_that(reservation.name).is_equal_to(input_data["name"])
        assert_that(reservation.description).is_equal_to(input_data["description"])
        assert_that(reservation.purpose).is_equal_to(self.purpose)
        assert_that(reservation.buffer_time_after).is_equal_to(
            self.reservation_unit.buffer_time_after
        )
        assert_that(reservation.buffer_time_before).is_equal_to(
            self.reservation_unit.buffer_time_before
        )

    @patch(
        "reservation_units.utils.reservation_unit_reservation_scheduler"
        + ".ReservationUnitReservationScheduler.is_reservation_unit_open"
    )
    @patch(
        "reservation_units.utils.reservation_unit_reservation_scheduler."
        + "ReservationUnitReservationScheduler.get_conflicting_open_application_round"
    )
    @patch(
        "reservation_units.utils.reservation_unit_reservation_scheduler."
        + "ReservationUnitReservationScheduler.get_reservation_unit_possible_start_times"
    )
    def test_creating_reservation_copies_max_buffer_times_from_multiple_reservation_units(
        self,
        mock_get_reservation_unit_possible_start_times,
        mock_get_conflicting_open_application_round,
        mock_is_open,
        mock_periods,
        mock_opening_hours,
    ):
        mock_is_open.return_value = True
        mock_get_conflicting_open_application_round.return_value = None
        mock_get_reservation_unit_possible_start_times.return_value = [
            datetime.datetime.now(tz=DEFAULT_TIMEZONE)
        ]
        sku = "340026__2652000155___44_10000100"
        self.reservation_unit.sku = sku
        self.reservation_unit.save(update_fields=["sku"])
        res_unit_too = ReservationUnitFactory(
            buffer_time_before=datetime.timedelta(minutes=90),
            buffer_time_after=None,
            sku=sku,
        )
        res_unit_another = ReservationUnitFactory(
            buffer_time_before=None,
            buffer_time_after=datetime.timedelta(minutes=15),
            sku=sku,
        )

        self.client.force_login(self.regular_joe)
        input_data = self.get_valid_input_data()
        input_data["reservationUnitPks"].extend([res_unit_too.id, res_unit_another.id])
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("reservation").get("pk")
        ).is_not_none()
        pk = content.get("data").get("createReservation").get("reservation").get("pk")
        reservation = Reservation.objects.get(id=pk)
        assert_that(reservation).is_not_none()
        assert_that(reservation.buffer_time_after).is_equal_to(
            self.reservation_unit.buffer_time_after
        )
        assert_that(reservation.buffer_time_before).is_equal_to(
            res_unit_too.buffer_time_before
        )

    def test_creating_reservation_without_optional_fields_succeeds(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        input_data = self.get_valid_input_data()
        optional_fields = [
            "reserveeType",
            "reserveeFirstName",
            "reserveeLastName",
            "reserveeOrganisationName",
            "reserveePhone",
            "reserveeEmail",
            "reserveeId",
            "reserveeIsUnregisteredAssociation",
            "reserveeAddressStreet",
            "reserveeAddressCity",
            "reserveeAddressZip",
            "billingFirstName",
            "billingLastName",
            "billingPhone",
            "billingEmail",
            "billingAddressStreet",
            "billingAddressCity",
            "billingAddressZip",
            "homeCityPk",
            "ageGroupPk",
            "applyingForFreeOfCharge",
            "freeOfChargeReason",
            "name",
            "description",
            "numPersons",
            "purposePk",
        ]
        for field in optional_fields:
            input_data.pop(field)
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(Reservation.objects.exists()).is_true()

    def test_creating_reservation_price_fails(self, mock_periods, mock_opening_hours):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        input_data = self.get_valid_input_data()
        input_data["price"] = 10
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()
        assert_that(Reservation.objects.exists()).is_false()

    def test_creating_reservation_with_pk_fails(self, mock_periods, mock_opening_hours):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        input_data = self.get_valid_input_data()
        input_data["pk"] = 9999
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_not_none()
        assert_that(Reservation.objects.exists()).is_false()

    def test_create_fails_when_overlapping_reservation(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=datetime.datetime.now(),
            end=datetime.datetime.now() + datetime.timedelta(hours=2),
            state=STATE_CHOICES.CONFIRMED,
        )

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"]
        ).contains("Overlapping reservations are not allowed.")

    def test_create_fails_when_buffer_time_overlaps_reservation_before(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        begin = datetime.datetime.now() - datetime.timedelta(hours=2)
        end = begin + datetime.timedelta(hours=1)
        ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=begin,
            end=end,
            buffer_time_after=datetime.timedelta(hours=1, minutes=1),
            state=STATE_CHOICES.CONFIRMED,
        )

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation overlaps with reservation before due to buffer time.")

    def test_create_fails_when_buffer_time_overlaps_reservation_after(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        begin = datetime.datetime.now() + datetime.timedelta(hours=2)
        end = begin + datetime.timedelta(hours=1)
        ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=begin,
            end=end,
            buffer_time_before=datetime.timedelta(hours=1, minutes=1),
            state=STATE_CHOICES.CONFIRMED,
        )

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation overlaps with reservation after due to buffer time.")

    def test_create_fails_when_reservation_unit_buffer_time_overlaps_with_existing_reservation_before(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.buffer_time_before = datetime.timedelta(
            hours=1, minutes=1
        )
        self.reservation_unit.save()
        begin = datetime.datetime.now() - datetime.timedelta(hours=2)
        end = begin + datetime.timedelta(hours=1)
        ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=begin,
            end=end,
            state=STATE_CHOICES.CONFIRMED,
        )

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation overlaps with reservation before due to buffer time.")

    def test_create_fails_when_reservation_unit_buffer_time_overlaps_with_existing_reservation_after(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.buffer_time_after = datetime.timedelta(hours=1, minutes=1)
        self.reservation_unit.save()
        begin = datetime.datetime.now() + datetime.timedelta(hours=2)
        end = begin + datetime.timedelta(hours=1)
        ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=begin,
            end=end,
            state=STATE_CHOICES.CONFIRMED,
        )

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation overlaps with reservation after due to buffer time.")

    def test_create_fails_when_reservation_unit_closed_on_selected_time(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        input_data = self.get_valid_input_data()
        today = datetime.date.today()
        begin = datetime.datetime(today.year, today.month, today.day, 21, 0)
        end = begin + datetime.timedelta(hours=2)
        input_data["begin"] = begin.strftime("%Y%m%dT%H%M%SZ")
        input_data["end"] = end.strftime("%Y%m%dT%H%M%SZ")

        self.client.force_login(self.regular_joe)
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation unit is not open within desired reservation time.")

    def test_create_fails_when_reservation_unit_in_open_application_round(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        ApplicationRoundFactory(
            reservation_units=[self.reservation_unit],
            reservation_period_begin=datetime.date.today(),
            reservation_period_end=datetime.date.today() + datetime.timedelta(days=10),
        )

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("One or more reservation units are in open application round.")

    def test_create_fails_when_reservation_unit_max_reservation_duration_exceeds(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.max_reservation_duration = datetime.timedelta(minutes=30)
        self.reservation_unit.save()

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains(
            "Reservation duration exceeds one or more reservation unit's maximum duration."
        )

    def test_create_fails_when_reservation_unit_min_reservation_duration_subsides(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.max_reservation_duration = None
        self.reservation_unit.min_reservation_duration = datetime.timedelta(hours=2)
        self.reservation_unit.save()

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains(
            "Reservation duration less than one or more reservation unit's minimum duration."
        )

    def test_create_succeeds_when_start_time_matches_reservation_start_interval(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        intervals = [
            value for value, _ in ReservationUnit.RESERVATION_START_INTERVAL_CHOICES
        ]
        for interval, interval_minutes in zip(intervals, [15, 30, 60, 90]):
            input_data = self.get_valid_input_data()
            self.reservation_unit.reservation_start_interval = interval
            self.reservation_unit.save(update_fields=["reservation_start_interval"])
            begin = datetime.datetime.now() + datetime.timedelta(
                minutes=interval_minutes
            )
            input_data["begin"] = begin.strftime("%Y%m%dT%H%M%SZ")
            response = self.query(self.get_create_query(), input_data=input_data)
            content = json.loads(response.content)
            assert_that(content.get("errors")).is_none()
            payload = content.get("data").get("createReservation", {})
            assert_that(payload.get("errors")).is_none()
            Reservation.objects.get(pk=payload["reservation"]["pk"]).delete()

    def test_create_fails_when_start_time_does_not_match_reservation_start_interval(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        intervals = [
            value for value, _ in ReservationUnit.RESERVATION_START_INTERVAL_CHOICES
        ]
        for interval, interval_minutes in zip(intervals, [15, 30, 60, 90]):
            input_data = self.get_valid_input_data()
            self.reservation_unit.reservation_start_interval = interval
            self.reservation_unit.save(update_fields=["reservation_start_interval"])
            begin = datetime.datetime.now() + datetime.timedelta(
                minutes=interval_minutes + 1
            )
            input_data["begin"] = begin.strftime("%Y%m%dT%H%M%SZ")
            response = self.query(self.get_create_query(), input_data=input_data)
            content = json.loads(response.content)
            assert_that(content.get("errors")).is_none()
            payload = content.get("data").get("createReservation", {})
            assert_that(payload.get("errors")).is_not_none()
            assert_that(payload.get("errors")[0]["messages"]).contains(
                f"Reservation start time does not match the allowed interval of {interval_minutes} minutes."
            )

    def test_create_fails_when_reservation_unit_reservation_begin_in_future(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.reservation_begins = datetime.datetime.now(
            tz=DEFAULT_TIMEZONE
        ) + datetime.timedelta(days=10)
        self.reservation_unit.save()

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation unit is not reservable within this reservation time.")

    def test_create_fails_when_reservation_unit_reservation_end_in_past(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.reservation_ends = datetime.datetime.now(
            tz=DEFAULT_TIMEZONE
        ) - datetime.timedelta(days=10)
        self.reservation_unit.save()

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"][0]
        ).contains("Reservation unit is not reservable within this reservation time.")

    def test_create_success_when_reservation_unit_reservation_begin_in_past(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.reservation_begins = datetime.datetime.now(
            tz=DEFAULT_TIMEZONE
        ) - datetime.timedelta(days=10)
        self.reservation_unit.save()

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_none()
        reservation = Reservation.objects.filter(
            id=content.get("data").get("createReservation").get("reservation").get("pk")
        ).first()
        assert_that(reservation).is_not_none()

    def test_create_success_when_reservation_unit_reservation_end_in_future(
        self, mock_periods, mock_opening_hours
    ):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.reservation_unit.reservation_ends = datetime.datetime.now(
            tz=DEFAULT_TIMEZONE
        ) + datetime.timedelta(days=10)
        self.reservation_unit.save()

        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_none()
        reservation = Reservation.objects.filter(
            id=content.get("data").get("createReservation").get("reservation").get("pk")
        ).first()
        assert_that(reservation).is_not_none()

    def test_create_fails_when_not_logged_in(self, mock_periods, mock_opening_hours):
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_not_none()
        assert_that(content.get("errors")[0].get("message")).is_equal_to(
            "No permission to mutate"
        )

    def test_create_success_when_reservation_date_over_next_spring(
        self, mock_periods, mock_opening_hours
    ):
        """In reservation creation it is needed to use opening_hours_end date
        parameter in ReservationUnitReservationScheduler initialization to get
        the possible opening hours from beyond next spring which is what the scheduler
        class defaults to.
        """
        opening_hours_data = self.get_mocked_opening_hours()
        opening_hours_data[0]["date"] = datetime.date(2022, 6, 15)
        mock_opening_hours.return_value = opening_hours_data

        res_start = datetime.datetime(2022, 6, 15, 15, 0)
        valid_data = self.get_valid_input_data()
        valid_data["begin"] = res_start.strftime("%Y%m%dT%H%M%SZ")
        valid_data["end"] = (res_start + datetime.timedelta(hours=1)).strftime(
            "%Y%m%dT%H%M%SZ"
        )
        self.client.force_login(self.regular_joe)
        response = self.query(self.get_create_query(), input_data=valid_data)
        content = json.loads(response.content)

        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("reservation").get("pk")
        ).is_not_none()
        pk = content.get("data").get("createReservation").get("reservation").get("pk")
        reservation = Reservation.objects.get(id=pk)
        assert_that(reservation).is_not_none()

    def test_creating_reservation_succeeds_when_under_max_reservations_per_user(
        self, mock_periods, mock_opening_hours
    ):
        self.reservation_unit.max_reservations_per_user = 1
        self.reservation_unit.save(update_fields=["max_reservations_per_user"])
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_none()
        assert_that(Reservation.objects.exists()).is_true()

    def test_creating_reservation_fails_when_max_reservations_per_user_reached(
        self, mock_periods, mock_opening_hours
    ):
        self.reservation_unit.max_reservations_per_user = 1
        self.reservation_unit.save(update_fields=["max_reservations_per_user"])
        existing_reservation = ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=datetime.datetime.now() + datetime.timedelta(hours=24),
            end=datetime.datetime.now() + datetime.timedelta(hours=25),
            state=STATE_CHOICES.CONFIRMED,
            user=self.regular_joe,
        )
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"]
        ).contains(
            "Maximum number of active reservations for this reservation unit exceeded."
        )
        assert_that(
            Reservation.objects.exclude(pk=existing_reservation.pk).exists()
        ).is_false()

    def test_old_reservations_are_not_counted_towards_max_reservations_per_user(
        self, mock_periods, mock_opening_hours
    ):
        self.reservation_unit.max_reservations_per_user = 1
        self.reservation_unit.save(update_fields=["max_reservations_per_user"])
        ReservationFactory(
            reservation_unit=[self.reservation_unit],
            begin=datetime.datetime.now() - datetime.timedelta(hours=25),
            end=datetime.datetime.now() - datetime.timedelta(hours=24),
            state=STATE_CHOICES.CONFIRMED,
            user=self.regular_joe,
        )
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_none()
        assert_that(Reservation.objects.exists()).is_true()

    def test_creating_reservation_copies_sku_from_reservation_unit(
        self, mock_periods, mock_opening_hours
    ):
        self.reservation_unit.sku = "340026__2652000155___44_10000117"
        self.reservation_unit.save(update_fields=["sku"])
        mock_opening_hours.return_value = self.get_mocked_opening_hours()
        self.client.force_login(self.regular_joe)
        response = self.query(
            self.get_create_query(), input_data=self.get_valid_input_data()
        )
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_none()
        reservation = Reservation.objects.get()
        assert_that(reservation.sku).is_equal_to(self.reservation_unit.sku)

    def test_creating_reservation_fails_if_sku_is_ambiguous(
        self, mock_periods, mock_opening_hours
    ):
        resunit1 = ReservationUnitFactory(sku="340026__2652000155___44_10000001")
        resunit2 = ReservationUnitFactory(sku="340026__2652000155___44_10000002")
        input_data = self.get_valid_input_data()
        input_data["reservationUnitPks"] = [resunit1.pk, resunit2.pk]

        def get_mocked_opening_hours(origin_ids, *args):
            if str(resunit1.uuid) in origin_ids:
                return self.get_mocked_opening_hours(resunit1)
            return self.get_mocked_opening_hours(resunit2)

        mock_opening_hours.side_effect = get_mocked_opening_hours
        self.client.force_login(self.regular_joe)
        response = self.query(self.get_create_query(), input_data=input_data)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")
        ).is_not_none()
        assert_that(
            content.get("data").get("createReservation").get("errors")[0]["messages"]
        ).contains("An ambiguous SKU cannot be assigned for this reservation.")
