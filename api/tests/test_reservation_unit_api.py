import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_reservation_unit_exists(user_api_client, reservation_unit):
    reservation_unit.name = "Studiokompleksi"
    reservation_unit.save()
    response = user_api_client.get(reverse("reservationunit-list"))
    assert response.status_code == 200
    assert response.data[0]["name"] == "Studiokompleksi"


@pytest.mark.django_db
def test_reservation_unit_purpose_filter(
    user_api_client, reservation_unit, reservation_unit2, purpose, purpose2
):
    reservation_unit.purposes.set([purpose])
    reservation_unit2.purposes.set([purpose2])
    response = user_api_client.get(reverse("reservationunit-list"))
    assert response.status_code == 200
    assert len(response.data) == 2

    url_with_filter = f"{reverse('reservationunit-list')}?purpose={purpose.pk}"
    filtered_response = user_api_client.get(url_with_filter)
    assert filtered_response.status_code == 200
    assert len(filtered_response.data) == 1
    assert filtered_response.data[0]["name"] == reservation_unit.name

    # Filter should work with multiple query parameters
    url_with_filter = (
        f"{reverse('reservationunit-list')}?purpose={purpose.pk}&purpose={purpose2.pk}"
    )
    filtered_response = user_api_client.get(url_with_filter)
    assert filtered_response.status_code == 200
    assert len(filtered_response.data) == 2
