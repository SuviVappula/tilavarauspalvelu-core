import json

import snapshottest
from assertpy import assert_that

from api.graphql.tests.base import GrapheneTestCaseBase
from reservations.tests.factories import ReservationDenyReasonFactory


class ReservationDenyReasonsQueryTestCase(GrapheneTestCaseBase, snapshottest.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.reason = ReservationDenyReasonFactory(
            reason_fi="fi", reason_sv="sv", reason_en="en"
        )

    def test_getting_reservation_deny_reasons_for_logged_in_user(self):
        self.client.force_login(self.regular_joe)
        response = self.query(
            """
            query {
                reservationDenyReasons {
                    edges {
                        node {
                            reasonFi
                            reasonSv
                            reasonEn
                        }
                    }
                }
            }
            """
        )
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        self.assertMatchSnapshot(content)

    def test_getting_reservation_deny_reasons_for_not_logged_in_user(self):
        response = self.query(
            """
            query {
                reservationDenyReasons {
                    edges {
                        node {
                            reasonFi
                            reasonSv
                            reasonEn
                        }
                    }
                }
            }
            """
        )
        assert_that(response.status_code).is_equal_to(200)
        content = json.loads(response.content)
        assert_that(content.get("errors")).is_none()
        assert_that(
            content.get("data").get("reservationDenyReasons").get("edges")
        ).is_empty()
