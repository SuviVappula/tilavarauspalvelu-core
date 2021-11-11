import datetime
import json
from unittest import mock

import snapshottest
from assertpy import assert_that
from django.conf import settings
from django.test import override_settings
from django.utils.timezone import get_default_timezone
from freezegun import freeze_time
from rest_framework.test import APIClient

from api.graphql.tests.base import GrapheneTestCaseBase
from applications.tests.factories import ApplicationRoundFactory
from opening_hours.enums import State
from opening_hours.errors import HaukiAPIError
from opening_hours.hours import TimeElement
from opening_hours.resources import Resource as HaukiResource
from reservation_units.models import ReservationUnit
from reservation_units.tests.factories import (
    EquipmentFactory,
    KeywordCategoryFactory,
    KeywordGroupFactory,
    ReservationUnitFactory,
    ReservationUnitPurposeFactory,
    ReservationUnitTypeFactory,
)
from reservations.models import STATE_CHOICES
from reservations.tests.factories import ReservationFactory
from resources.tests.factories import ResourceFactory
from services.tests.factories import ServiceFactory
from spaces.tests.factories import SpaceFactory, UnitFactory

DEFAULT_TIMEZONE = get_default_timezone()


@freeze_time("2021-05-03")
class ReservationUnitTestCase(GrapheneTestCaseBase, snapshottest.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.type = ReservationUnitTypeFactory(name="Test type")
        large_space = SpaceFactory(
            max_persons=100, name="Large space", surface_area=100
        )
        small_space = SpaceFactory(max_persons=10, name="Small space", surface_area=50)
        cls.reservation_unit = ReservationUnitFactory(
            name="Test name",
            reservation_unit_type=cls.type,
            uuid="3774af34-9916-40f2-acc7-68db5a627710",
            spaces=[large_space, small_space],
        )

        cls.api_client = APIClient()

    def test_getting_reservation_units(self):
        self.maxDiff = None
        self._client.force_login(self.regular_joe)
        response = self.query(
            """
            query {
                reservationUnits {
                    edges {
                        node {
                            nameFi
                            descriptionFi
                            spaces {
                              nameFi
                            }
                            resources {
                              nameFi
                            }
                            services {
                              nameFi
                            }
                            requireIntroduction
                            purposes {
                              nameFi
                            }
                            images {
                              imageUrl
                              mediumUrl
                              smallUrl
                            }
                            location {
                              longitude
                              latitude
                            }
                            maxPersons
                            surfaceArea
                            reservationUnitType {
                              nameFi
                            }
                            termsOfUseFi
                            equipment {
                              nameFi
                            }
                            contactInformationFi
                            reservations {
                              begin
                              end
                              state
                            }
                            applicationRounds {
                              nameFi
                              targetGroup
                              allocating
                              applicationPeriodBegin
                              applicationPeriodEnd
                              reservationPeriodBegin
                              reservationPeriodEnd
                              publicDisplayBegin
                              publicDisplayEnd
                              criteriaFi
                            }
                          }
                        }
                    }
                }
            """
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_should_be_able_to_find_by_pk(self):
        query = (
            f"{{\n"
            f"reservationUnitByPk(pk: {self.reservation_unit.id}) {{\n"
            f"id nameFi pk\n"
            f"}}"
            f"}}"
        )
        response = self.query(query)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("reservationUnitByPk").get("pk")
        ).is_equal_to(self.reservation_unit.id)

    def test_getting_hauki_url(self):
        settings.HAUKI_SECRET = "HAUKISECRET"
        settings.HAUKI_ADMIN_UI_URL = "https://test.com"
        settings.HAUKI_ORIGIN_ID = "origin"
        settings.HAUKI_ORGANISATION_ID = "ORGANISATION"
        self.maxDiff = None
        query = (
            f"{{\n"
            f"reservationUnitByPk(pk: {self.reservation_unit.id}) {{\n"
            f"nameFi\n"
            f"haukiUrl{{url}}"
            f"}}"
            f"}}"
        )
        response = self.query(query)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_should_error_when_not_found_by_pk(self):
        query = (
            f"{{\n"
            f"reservationUnitByPk(pk: {self.reservation_unit.id + 666}) {{\n"
            f"id\n"
            f"}}"
            f"}}"
        )
        response = self.query(query)

        content = json.loads(response.content)
        errors = content.get("errors")
        assert_that(len(errors)).is_equal_to(1)
        assert_that(errors[0].get("message")).is_equal_to(
            "No ReservationUnit matches the given query."
        )

    @override_settings(HAUKI_ORIGIN_ID="1234", HAUKI_API_URL="url")
    @mock.patch("opening_hours.utils.opening_hours_client.get_opening_hours")
    @mock.patch("opening_hours.hours.make_hauki_get_request")
    def test_opening_hours(self, mock_periods, mock_opening_times):
        mock_opening_times.return_value = get_mocked_opening_hours(
            self.reservation_unit.uuid
        )
        mock_periods.return_value = get_mocked_periods()
        query = (
            f"{{\n"
            f"reservationUnitByPk(pk: {self.reservation_unit.id}) {{\n"
            f"id\n"
            f'openingHours(periods:true openingTimes:true startDate:"2020-01-01" endDate:"2022-01-01")'
            f"{{openingTimes{{date startTime endTime}} openingTimePeriods{{timeSpans{{startTime}}}}"
            f"}}"
            f"}}"
            f"}}"
        )
        response = self.query(query)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data")
            .get("reservationUnitByPk")
            .get("openingHours")
            .get("openingTimePeriods")[0]
            .get("timeSpans")
        ).is_not_empty()

        assert_that(
            content.get("data")
            .get("reservationUnitByPk")
            .get("openingHours")
            .get("openingTimes")
        ).is_not_empty()
        assert_that(
            content.get("data")
            .get("reservationUnitByPk")
            .get("openingHours")
            .get("openingTimes")[0]["startTime"]
        ).is_equal_to("10:00:00+00:00")
        assert_that(
            content.get("data")
            .get("reservationUnitByPk")
            .get("openingHours")
            .get("openingTimes")[0]["endTime"]
        ).is_equal_to("22:00:00+00:00")

    def test_filtering_by_type(self):
        response = self.query(
            f"query {{"
            f"reservationUnits(reservationUnitType:{self.type.id}){{"
            f"edges {{"
            f"node {{"
            f"nameFi "
            f"reservationUnitType {{"
            f"nameFi"
            f"}}"
            f"}}"
            f"}}"
            f"}}"
            f"}}"
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_filtering_by_purpose(self):
        purpose = ReservationUnitPurposeFactory(name="Test purpose")
        self.reservation_unit.purposes.set([purpose])
        response = self.query(
            f"""
            query {{
                reservationUnits(purposes: {purpose.pk}) {{
                    edges {{
                        node {{
                            nameFi purposes {{
                                nameFi
                            }}
                        }}
                    }}
                }}
            }}
            """
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_filtering_by_type_not_found(self):
        response = self.query(
            """
            query {
                reservationUnits(reservationUnitType:345987){
                edges {
                    node {
                        nameFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_empty()

    def test_filtering_by_max_persons(self):
        response = self.query(
            """
            query {
                reservationUnits(maxPersonsLte:120, maxPersonsGte:60) {
                    edges {
                        node{
                            nameFi maxPersons
                        }
                    }
                }
            }
            """
        )
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_filtering_by_max_persons_not_found(self):
        response = self.query(
            """
            query {
                reservationUnits(maxPersonsLte:20, maxPersonsGte:15) {
                    edges {
                        node{
                            nameFi maxPersons
                        }
                    }
                }
            }
            """
        )
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def content_is_empty(self, content):
        return len(content["data"]["reservationUnits"]["edges"]) == 0

    def test_filtering_by_type_text(self):
        response = self.query(
            """
            query {
                reservationUnits(textSearch:"Test type"){
                edges {
                    node {
                        nameFi
                        reservationUnitType {
                            nameFi
                        }
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

        response = self.query(
            """
            query {
                reservationUnits(textSearch:"Nonexisting type"){
                edges {
                    node {
                        nameFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_true()

    def test_filtering_by_reservation_unit_name(self):
        response = self.query(
            """
            query {
                reservationUnits(textSearch:"Test name"){
                edges {
                    node {
                        nameFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

        response = self.query(
            """
            query {
                reservationUnits(textSearch:"Nonexisting name"){
                edges {
                    node {
                        nameFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_true()

    def test_filtering_by_reservation_unit_description(self):
        self.reservation_unit.description_fi = "Lorem ipsum"
        self.reservation_unit.save()
        response = self.query(
            """
            query {
                reservationUnits(textSearch:"Lorem ipsum"){
                edges {
                    node {
                        nameFi
                        descriptionFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

        response = self.query(
            """
            query {
                reservationUnits(textSearch:"Dolor sit"){
                edges {
                    node {
                        nameFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_true()

    def test_filtering_by_space_name(self):
        space = SpaceFactory(name="space name")
        self.reservation_unit.spaces.set([space])
        self.reservation_unit.save()

        response = self.query(
            """
            query {
                reservationUnits(textSearch:"space name"){
                edges {
                    node {
                        nameFi
                        spaces{nameFi}
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

        response = self.query(
            """
            query {
                reservationUnits(textSearch:"not a space name"){
                edges {
                    node {
                        nameFi
                    }
                }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_true()

    def test_filtering_by_keyword_group(self):
        category = KeywordCategoryFactory()

        keyword_group = KeywordGroupFactory(keyword_category=category, name="Sports")
        self.reservation_unit.keyword_groups.set([keyword_group])
        self.reservation_unit.save()
        response = self.query(
            f"query {{"
            f"reservationUnits( keywordGroups:{keyword_group.id}){{"
            f"edges {{"
            f"node {{"
            f"nameFi\n"
            f"keywordGroups{{nameFi}}"
            f"}}"
            f"}}"
            f"}}"
            f"}}"
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

        response = self.query(
            f"query {{"
            f"reservationUnits( keywordGroups:{keyword_group.id+214979}){{"
            f"edges {{"
            f"node {{"
            f"nameFi\n"
            f"keywordGroups{{nameFi}}"
            f"}}"
            f"}}"
            f"}}"
            f"}}"
        )

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_empty()

    def test_filtering_by_reservation_timestamps(self):
        now = datetime.datetime.now().astimezone()
        one_hour = datetime.timedelta(hours=1)
        matching_reservation = ReservationFactory(
            begin=now,
            end=now + one_hour,
            state=STATE_CHOICES.CREATED,
        )
        other_reservation = ReservationFactory(
            begin=datetime.datetime(2021, 1, 1),
            end=datetime.datetime(2021, 1, 2),
        )
        self.reservation_unit.reservation_set.set(
            [matching_reservation, other_reservation]
        )
        self.reservation_unit.save()

        self._client.force_login(self.regular_joe)
        response = self.query(
            """
            query {
                reservationUnits {
                    edges {
                        node {
                            nameFi
                            reservations(from: "2021-05-03", to: "2021-05-04") {
                                begin
                                end
                                state
                            }
                        }
                    }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_filtering_by_reservation_state(self):
        now = datetime.datetime.now().astimezone()
        one_hour = datetime.timedelta(hours=1)
        matching_reservation = ReservationFactory(
            begin=now,
            end=now + one_hour,
            state=STATE_CHOICES.CREATED,
        )
        other_reservation = ReservationFactory(
            begin=now + one_hour,
            end=now + one_hour + one_hour,
            state=STATE_CHOICES.CANCELLED,
        )
        self.reservation_unit.reservation_set.set(
            [matching_reservation, other_reservation]
        )
        self.reservation_unit.save()
        self._client.force_login(self.regular_joe)
        response = self.query(
            """
            query {
                reservationUnits {
                    edges {
                        node {
                            nameFi
                            reservations(state: "created") {
                                begin
                                end
                                state
                            }
                        }
                    }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_filtering_by_multiple_reservation_states(self):
        now = datetime.datetime.now().astimezone()
        one_hour = datetime.timedelta(hours=1)
        two_hours = datetime.timedelta(hours=2)
        matching_reservations = [
            ReservationFactory(
                begin=now, end=now + one_hour, state=STATE_CHOICES.CREATED
            ),
            ReservationFactory(
                begin=now + one_hour, end=now + two_hours, state=STATE_CHOICES.CONFIRMED
            ),
        ]
        other_reservation = ReservationFactory(
            begin=now + two_hours,
            end=now + two_hours + one_hour,
            state=STATE_CHOICES.CANCELLED,
        )
        self.reservation_unit.reservation_set.set(
            matching_reservations + [other_reservation]
        )
        self.reservation_unit.save()

        self._client.force_login(self.regular_joe)
        response = self.query(
            """
            query {
                reservationUnits {
                    edges {
                        node {
                            nameFi
                            reservations(state: ["created", "confirmed"]) {
                                begin
                                end
                                state
                            }
                        }
                    }
                }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_filtering_by_active_application_rounds(self):
        now = datetime.datetime.now().astimezone()
        one_hour = datetime.timedelta(hours=1)
        matching_round = ApplicationRoundFactory(
            name="Test Round",
            application_period_begin=now - one_hour,
            application_period_end=now + one_hour,
        )
        other_round = ApplicationRoundFactory(
            application_period_begin=datetime.datetime(2021, 1, 1, 12).astimezone(),
            application_period_end=datetime.datetime(2021, 1, 1, 13).astimezone(),
        )
        self.reservation_unit.application_rounds.set([matching_round, other_round])
        self.reservation_unit.save()
        response = self.query(
            """
            query {
              reservationUnits {
                edges {
                  node {
                    applicationRounds(active: true) {
                      nameFi
                    }
                  }
                }
              }
            }
            """
        )

        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_getting_manually_given_surface_area(self):
        self.reservation_unit.surface_area = 500
        self.reservation_unit.save()
        response = self.query(
            """
            query {
                reservationUnits {
                    edges {
                        node {
                            surfaceArea
                        }
                    }
                }
            }
            """
        )
        content = json.loads(response.content)
        assert_that(self.content_is_empty(content)).is_false()
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)


def get_mocked_opening_hours(uuid):
    resource_id = f"{settings.HAUKI_ORIGIN_ID}:{uuid}"
    return [
        {
            "timezone": DEFAULT_TIMEZONE,
            "resource_id": resource_id,
            "origin_id": str(uuid),
            "date": datetime.date(2020, 1, 1),
            "times": [
                TimeElement(
                    start_time=datetime.time(hour=10),
                    end_time=datetime.time(hour=22),
                    end_time_on_next_day=False,
                    resource_state=State.WITH_RESERVATION,
                    periods=[1, 2, 3, 4],
                ),
            ],
        },
        {
            "timezone": DEFAULT_TIMEZONE,
            "resource_id": resource_id,
            "origin_id": str(uuid),
            "date": datetime.date(2020, 1, 2),
            "times": [
                TimeElement(
                    start_time=datetime.time(hour=10),
                    end_time=datetime.time(hour=22),
                    end_time_on_next_day=False,
                    resource_state=State.WITH_RESERVATION,
                    periods=[
                        1,
                    ],
                ),
            ],
        },
    ]


def get_mocked_periods():
    data = [
        {
            "id": 38600,
            "resource": 26220,
            "name": {"fi": "Vakiovuorot", "sv": "", "en": ""},
            "description": {"fi": "", "sv": "", "en": ""},
            "start_date": "2020-01-01",
            "end_date": None,
            "resource_state": "undefined",
            "override": False,
            "origins": [],
            "created": "2021-05-07T13:01:30.477693+03:00",
            "modified": "2021-05-07T13:01:30.477693+03:00",
            "time_span_groups": [
                {
                    "id": 29596,
                    "period": 38600,
                    "time_spans": [
                        {
                            "id": 39788,
                            "group": 29596,
                            "name": {"fi": None, "sv": None, "en": None},
                            "description": {"fi": None, "sv": None, "en": None},
                            "start_time": "09:00:00",
                            "end_time": "21:00:00",
                            "end_time_on_next_day": False,
                            "full_day": False,
                            "weekdays": [6],
                            "resource_state": "open",
                            "created": "2021-05-07T13:01:30.513468+03:00",
                            "modified": "2021-05-07T13:01:30.513468+03:00",
                        },
                        {
                            "id": 39789,
                            "group": 29596,
                            "name": {
                                "fi": None,
                                "sv": None,
                                "en": None,
                            },
                            "description": {"fi": None, "sv": None, "en": None},
                            "start_time": "09:00:00",
                            "end_time": "21:00:00",
                            "end_time_on_next_day": False,
                            "full_day": False,
                            "weekdays": [7],
                            "resource_state": "open",
                            "created": "2021-05-07T13:01:30.530932+03:00",
                            "modified": "2021-05-07T13:01:30.530932+03:00",
                        },
                    ],
                    "rules": [],
                    "is_removed": False,
                }
            ],
        }
    ]
    return data


class ReservationUnitMutationsTestCaseBase(GrapheneTestCaseBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.unit = UnitFactory()
        cls.purpose = ReservationUnitPurposeFactory()
        cls.space = SpaceFactory(unit=cls.unit)
        cls.resource = ResourceFactory()
        cls.reservation_unit_type = ReservationUnitTypeFactory()
        cls.service = ServiceFactory()

    def setUp(self):
        self._client.force_login(self.general_admin)


class ReservationUnitCreateAsDraftTestCase(ReservationUnitMutationsTestCaseBase):
    def get_create_query(self):
        return """
        mutation createReservationUnit($input: ReservationUnitCreateMutationInput!) {
            createReservationUnit(input: $input){
                pk
                errors {
                    messages field
                }
            }
        }
        """

    def test_create(self):
        data = {
            "isDraft": True,
            "nameFi": "Resunit name",
            "nameEn": "English name",
            "descriptionFi": "desc",
            "unitPk": self.unit.pk,
        }
        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))

    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    @override_settings(HAUKI_EXPORT_ENABLED=True)
    def test_send_resource_to_hauki_is_not_called(self, send_resource_mock):
        data = {
            "isDraft": True,
            "nameFi": "Resunit name",
            "nameEn": "English name",
            "descriptionFi": "desc",
            "unitPk": self.unit.pk,
        }

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(send_resource_mock.call_count).is_equal_to(0)

    def test_create_errors_without_unit_pk(self):
        data = {"isDraft": True, "nameFi": "Resunit name"}
        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

    def test_create_errors_on_empty_name(self):
        data = {
            "isDraft": True,
            "nameFi": "",
            "nameEn": "English name",
            "descriptionFi": "desc",
            "unitPk": self.unit.id,
        }
        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_none()

    def test_create_with_minimum_fields_success(self):
        data = {
            "isDraft": True,
            "nameFi": "Resunit name",
            "unitPk": self.unit.id,
        }
        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))

    def test_create_without_is_draft_with_name_and_unit_fails(self):
        data = {
            "nameFi": "Resunit name",
            "unitPk": self.unit.id,
        }
        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()

    def test_regular_user_cannot_create(self):
        self._client.force_login(self.regular_joe)
        data = {"isDraft": True, "nameFi": "Resunit name", "unitPk": self.unit.id}
        response = self.query(self.get_create_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_none()


class ReservationUnitCreateAsNotDraftTestCase(ReservationUnitMutationsTestCaseBase):
    """For publish"""

    def get_create_query(self):
        return """
        mutation createReservationUnit($input: ReservationUnitCreateMutationInput!) {
            createReservationUnit(input: $input){
                pk
                errors {
                    messages field
                }
            }
        }
        """

    def get_valid_data(self):
        return {
            "isDraft": False,
            "nameFi": "Resunit name",
            "nameEn": "English name",
            "nameSv": "Swedish name",
            "descriptionFi": "descFi",
            "descriptionEn": "descEn",
            "descriptionSv": "descSV",
            "termsOfUseFi": "termsFi",
            "termsOfUseEn": "termsEn",
            "termsOfUseSv": "termsSv",
            "contactInformationFi": "contactFi",
            "contactInformationEn": "contactEn",
            "contactInformationSv": "contactSv",
            "spacePks": [self.space.id],
            "resourcePks": [self.resource.id],
            "servicePks": [self.service.id],
            "unitPk": self.unit.id,
            "reservationUnitTypePk": self.reservation_unit_type.id,
            "surfaceArea": 100,
            "maxPersons": 10,
            "bufferTimeBetweenReservations": "1:00:00",
        }

    def test_create(self):
        data = self.get_valid_data()
        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.is_draft).is_false()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))
        assert_that(res_unit.name_fi).is_equal_to(data.get("nameFi"))
        assert_that(res_unit.name_en).is_equal_to(data.get("nameEn"))
        assert_that(res_unit.name_sv).is_equal_to(data.get("nameSv"))
        assert_that(res_unit.description_fi).is_equal_to(data.get("descriptionFi"))
        assert_that(res_unit.description_en).is_equal_to(data.get("descriptionEn"))
        assert_that(res_unit.description_sv).is_equal_to(data.get("descriptionSv"))
        assert_that(res_unit.spaces.first().id).is_equal_to(self.space.id)
        assert_that(res_unit.resources.first().id).is_equal_to(self.resource.id)
        assert_that(res_unit.services.first().id).is_equal_to(self.service.id)
        assert_that(res_unit.reservation_unit_type).is_equal_to(
            self.reservation_unit_type
        )
        assert_that(res_unit.surface_area).is_equal_to(data.get("surfaceArea"))
        assert_that(res_unit.max_persons).is_equal_to(data.get("maxPersons"))
        assert_that(res_unit.buffer_time_between_reservations).is_equal_to(
            datetime.timedelta(hours=1)
        )

    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    @override_settings(HAUKI_EXPORTS_ENABLED=True)
    def test_send_resource_to_hauki_called(self, send_resource_mock):
        res = HaukiResource(
            id=1,
            name="",
            description="",
            address=None,
            origin_data_source_name="Tilavarauspalvelu",
            origin_data_source_id="tvp",
            origin_id="",
            organization="department_id",
            parents=[],
            children=[],
            resource_type="",
        )
        send_resource_mock.return_value = res

        data = self.get_valid_data()
        response = self.query(self.get_create_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(send_resource_mock.call_count).is_equal_to(1)

    @override_settings(HAUKI_EXPORTS_ENABLED=True)
    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    def test_send_resource_to_hauki_errors_returns_error_message(
        self, send_resource_mock
    ):
        send_resource_mock.side_effect = HaukiAPIError()

        data = self.get_valid_data()
        response = self.query(self.get_create_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Sending reservation unit as resource to HAUKI failed."
        )
        assert_that(send_resource_mock.call_count).is_equal_to(1)
        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit.hauki_resource_id).is_none()

    def test_create_errors_on_empty_name_translations(self):
        data = self.get_valid_data()
        data["nameEn"] = ""
        data["nameSv"] = ""

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation units must have a translations."
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_missing_name_translations(self):
        data = self.get_valid_data()
        data.pop("nameSv")
        data.pop("nameEn")

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation units must have a translations."
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_empty_description_translations(self):
        data = self.get_valid_data()
        data["descriptionFi"] = ""
        data["descriptionSv"] = ""
        data["descriptionEn"] = ""

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation units must have a translations."
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_missing_description_translations(self):
        data = self.get_valid_data()
        data.pop("descriptionFi")
        data.pop("descriptionEn")
        data.pop("descriptionSv")

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation units must have a translations."
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_without_unit_pk(self):
        data = self.get_valid_data()
        data.pop("unitPk")

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_empty_space_and_missing_resource(self):
        data = self.get_valid_data()
        data.pop("resourcePks")
        data["spacePks"] = []

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation unit must have one or more space or resource defined"
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_empty_resource_and_missing_space(self):
        data = self.get_valid_data()
        data.pop("spacePks")
        data["resourcePks"] = []

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation unit must have one or more space or resource defined"
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_empty_space_and_resource(self):
        data = self.get_valid_data()
        data["resourcePks"] = []
        data["spacePks"] = []

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation unit must have one or more space or resource defined"
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_missing_space_and_resource(self):
        data = self.get_valid_data()
        data.pop("resourcePks")
        data.pop("spacePks")

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation unit must have one or more space or resource defined"
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_wrong_type_of_space_pk(self):
        data = self.get_valid_data()
        data["spacePks"] = "b"

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

    def test_create_errors_on_wrong_type_of_resource_pk(self):
        data = self.get_valid_data()
        data["resourcePks"] = "b"

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

    def test_create_errors_on_reservation_unit_type(self):
        data = self.get_valid_data()
        data.pop("reservationUnitTypePk")

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft reservation unit must have a reservation unit type."
        )
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_errors_on_wrong_reservation_unit_type(self):
        data = self.get_valid_data()
        data["reservationUnitTypePk"] = -15

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(ReservationUnit.objects.exists()).is_false()

    def test_create_with_multiple_spaces(self):
        space_too = SpaceFactory()
        data = self.get_valid_data()
        data["spacePks"] = [self.space.id, space_too.id]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))
        assert_that(list(res_unit.spaces.all().values_list("id", flat=True))).is_in(
            data.get("spacePks")
        )

    def test_create_with_multiple_purposes(self):
        purposes = ReservationUnitPurposeFactory.create_batch(5)
        data = self.get_valid_data()
        data["purposePks"] = [purpose.id for purpose in purposes]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))
        assert_that(list(res_unit.purposes.all().values_list("id", flat=True))).is_in(
            data.get("purposePks")
        )

    def test_create_errors_on_wrong_type_of_purpose_pk(self):
        data = self.get_valid_data()
        data["purposePks"] = ["b"]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

    def test_create_with_multiple_services(self):
        purposes = ServiceFactory.create_batch(5)
        data = self.get_valid_data()
        data["servicePks"] = [purpose.id for purpose in purposes]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))
        assert_that(list(res_unit.services.all().values_list("id", flat=True))).is_in(
            data.get("servicePks")
        )

    def test_create_errors_on_wrong_type_of_service_pk(self):
        data = self.get_valid_data()
        data["servicePks"] = ["b"]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

    def test_create_with_multiple_resources(self):
        resource = ResourceFactory()
        data = self.get_valid_data()
        data["resourcePks"] = [self.resource.id, resource.id]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))
        assert_that(list(res_unit.resources.all().values_list("id", flat=True))).is_in(
            data.get("resourcePks")
        )

    def test_create_with_multiple_equipments(self):
        equipments = EquipmentFactory.create_batch(5)
        data = self.get_valid_data()
        data["equipmentPks"] = [equipment.id for equipment in equipments]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("createReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_not_none()
        assert_that(res_unit.id).is_equal_to(res_unit_data.get("pk"))
        assert_that(list(res_unit.equipments.all().values_list("id", flat=True))).is_in(
            data.get("equipmentPks")
        )

    def test_create_errors_on_wrong_type_of_equipment_pk(self):
        data = self.get_valid_data()
        data["equipmentPks"] = ["b"]

        response = self.query(self.get_create_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(400)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

    def test_regular_user_cannot_create(self):
        self._client.force_login(self.regular_joe)
        data = self.get_valid_data()
        response = self.query(self.get_create_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

        res_unit = ReservationUnit.objects.first()
        assert_that(res_unit).is_none()


class ReservationUnitUpdateDraftTestCase(ReservationUnitMutationsTestCaseBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.res_unit = ReservationUnitFactory(
            is_draft=True,
            name="Resunit name",
            unit=cls.unit,
        )

    def get_update_query(self):
        return """
            mutation updateReservationUnit($input: ReservationUnitUpdateMutationInput!) {
                updateReservationUnit(input: $input){
                    pk
                    errors {
                        messages field
                    }
                }
            }
            """

    def get_valid_update_data(self):
        return {"pk": self.res_unit.pk}

    def test_update(self):
        data = self.get_valid_update_data()
        data["nameFi"] = "New name"

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(res_unit_data.get("errors")).is_none()

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.name_fi).is_equal_to("New name")

    def test_update_errors_with_empty_name(self):
        data = self.get_valid_update_data()
        data["nameFi"] = ""

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()

        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "nameFi is required for draft reservation units"
        )

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.name_fi).is_not_empty()

    def test_regular_user_cannot_update(self):
        self._client.force_login(self.regular_joe)
        data = self.get_valid_update_data()
        data["nameFi"] = "Better name in my opinion."
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.name).is_equal_to("Resunit name")

    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    @override_settings(HAUKI_EXPORTS_ENABLED=True)
    def test_send_resource_to_hauki_called_when_resource_id_exists(
        self, send_resource_mock
    ):
        self.res_unit.hauki_resource_id = "1"
        self.res_unit.save()

        data = self.get_valid_update_data()
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(send_resource_mock.call_count).is_equal_to(1)

    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    @override_settings(HAUKI_EXPORTS_ENABLED=False)
    def test_send_resource_to_hauki_not_called_when_exports_disabled(
        self, send_resource_mock
    ):
        data = self.get_valid_update_data()
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(send_resource_mock.call_count).is_equal_to(0)


class ReservationUnitUpdateNotDraftTestCase(ReservationUnitMutationsTestCaseBase):
    """For published resunits"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.res_unit = ReservationUnitFactory(
            is_draft=False,
            name_fi="Resunit name",
            name_en="Resunit name",
            name_sv="Resunit name",
            description_fi="Desc",
            description_en="Desc",
            description_sv="Desc",
            terms_of_use_fi="Terms",
            terms_of_use_sv="Terms",
            terms_of_use_en="Terms",
            contact_information_fi="Info",
            contact_information_sv="Info",
            contact_information_en="Info",
            reservation_unit_type=cls.reservation_unit_type,
            unit=cls.unit,
        )
        cls.res_unit.spaces.add(cls.space)
        cls.res_unit.resources.add(cls.resource)

    def setUp(self):
        super().setUp()
        self.res_unit.hauki_resource_id = None
        self.res_unit.save()

    def get_update_query(self):
        return """
        mutation updateReservationUnit($input: ReservationUnitUpdateMutationInput!) {
            updateReservationUnit(input: $input){
                pk
                errors {
                    messages field
                }
            }
        }
        """

    def get_valid_update_data(self):
        return {"pk": self.res_unit.pk}

    def test_update(self):
        data = self.get_valid_update_data()
        data["nameFi"] = "New name"

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.name_fi).is_equal_to("New name")

    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    @override_settings(HAUKI_EXPORTS_ENABLED=True)
    def test_send_resource_to_hauki_called_when_no_resource_id(
        self, send_resource_mock
    ):
        res = HaukiResource(
            id=1,
            name="",
            description="",
            address=None,
            origin_data_source_name="Tilavarauspalvelu",
            origin_data_source_id="tvp",
            origin_id="",
            organization="department_id",
            parents=[],
            children=[],
            resource_type="",
        )
        send_resource_mock.return_value = res

        data = self.get_valid_update_data()
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(send_resource_mock.call_count).is_equal_to(1)

    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    @override_settings(HAUKI_EXPORTS_ENABLED=True)
    def test_send_resource_to_hauki_called_when_resource_id_exists(
        self, send_resource_mock
    ):
        self.res_unit.hauki_resource_id = "1"
        self.res_unit.save()

        data = self.get_valid_update_data()
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(send_resource_mock.call_count).is_equal_to(1)

    @override_settings(HAUKI_EXPORTS_ENABLED=True)
    @mock.patch(
        "reservation_units.utils.hauki_exporter.ReservationUnitHaukiExporter.send_reservation_unit_to_hauki"
    )
    def test_send_resource_to_hauki_errors_returns_error_message(
        self, send_resource_mock
    ):
        send_resource_mock.side_effect = HaukiAPIError()

        data = self.get_valid_update_data()
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Sending reservation unit as resource to HAUKI failed."
        )
        assert_that(send_resource_mock.call_count).is_equal_to(1)

    def test_update_surface_area(self):
        expected_surface_area = 150
        data = self.get_valid_update_data()
        data["surfaceArea"] = expected_surface_area
        update_query = """
            mutation updateReservationUnit($input: ReservationUnitUpdateMutationInput!) {
                updateReservationUnit(input: $input) {
                    surfaceArea
                    errors {
                        messages
                        field
                    }
                }
            }
        """
        response = self.query(update_query, input_data=data)
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(content.get("errors")).is_none()
        assert_that(res_unit_data.get("errors")).is_none()
        assert_that(res_unit_data.get("surfaceArea")).is_equal_to(expected_surface_area)
        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.surface_area).is_equal_to(expected_surface_area)

    def test_errors_on_empty_name_translations(self):
        data = self.get_valid_update_data()
        data["nameEn"] = ""

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()

        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation units must have a translations."
        )

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.name_en).is_not_empty()

    def test_errors_on_empty_description_translations(self):
        data = self.get_valid_update_data()
        data["descriptionEn"] = ""

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()

        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(res_unit_data.get("errors")).is_not_none()

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.description_en).is_not_empty()

    def test_errors_on_empty_space_and_resource(self):
        data = self.get_valid_update_data()
        data["spacePks"] = []
        data["resourcePks"] = []

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()

        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(res_unit_data.get("errors")).is_not_none()
        assert_that(res_unit_data.get("errors")[0].get("messages")[0]).contains(
            "Not draft state reservation unit must have one or more space or resource defined"
        )

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.spaces.exists()).is_true()
        assert_that(self.res_unit.resources.exists()).is_true()

    def test_errors_on_empty_type(self):
        data = self.get_valid_update_data()
        data["reservationUnitTypePk"] = None

        response = self.query(self.get_update_query(), input_data=data)
        assert_that(response.status_code).is_equal_to(200)

        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()

        res_unit_data = content.get("data").get("updateReservationUnit")
        assert_that(res_unit_data.get("errors")).is_not_none()

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.reservation_unit_type).is_not_none()

    def test_regular_user_cannot_update(self):
        self._client.force_login(self.regular_joe)
        data = self.get_valid_update_data()
        data["nameFi"] = "Better name in my opinion."
        response = self.query(self.get_update_query(), input_data=data)

        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_not_none()

        self.res_unit.refresh_from_db()
        assert_that(self.res_unit.name).is_equal_to("Resunit name")
