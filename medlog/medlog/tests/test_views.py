from datetime import date, timedelta

import pytest
from core.models.day_log import DayLog
from core.models.medicine import Medicine
from core.models.user import User
from core.models.visit import Visit
from django.test import Client


@pytest.mark.django_db
def test_login_incorrect_data(client: Client) -> None:
    response = client.post(
        "/loginsubmit/", {"email": "test@test.de", "password": "test"}
    )
    assert response.status_code == 200
    assert "Invalid email or password" in response.context["form"].errors["__all__"]


@pytest.mark.django_db
def test_login_correct_data(
    client: Client, user: User, user_data: dict[str, str]
) -> None:
    response = client.post(
        "/loginsubmit/", {"email": user.email, "password": user_data["password"]}
    )
    assert response.__class__.__name__ == "HttpResponseClientRedirect"
    assert response.headers["HX-Redirect"] == "/dashboard"


@pytest.mark.django_db
def test_logout(authenticated_client: Client) -> None:
    assert authenticated_client.session._SessionBase__session_key is not None
    response = authenticated_client.get("/logout/")
    assert response.status_code == 302
    assert response.url == "/"
    assert authenticated_client.session._SessionBase__session_key is None


@pytest.mark.django_db
def test_add_medicines(authenticated_client: Client) -> None:
    # GET method not allowed
    response = authenticated_client.get("/dashboard/add-medicine/")
    assert response.status_code == 405

    # Correct data
    payload = {
        "marketing_name": "test",
        "latin_name": "test",
        "dose": 10,
        "dose_unit": "mg",
        "type": "preventive",
    }
    response = authenticated_client.post(
        "/dashboard/add-medicine/",
        payload,
    )
    assert response.status_code == 200
    assert response.__class__.__name__ == "HttpResponseClientRedirect"
    assert response.headers["HX-Redirect"] == "/dashboard"
    assert Medicine.objects.all().count() == 1
    medicine_db = Medicine.objects.first()
    for key, value in payload.items():
        assert getattr(medicine_db, key) == value

    # Incorrect data
    payload = {
        "marketing_name": "test",
        "dose": 10,
        "dose_unit": "mg",
        "type": "test",
    }
    response = authenticated_client.post(
        "/dashboard/add-medicine/",
        payload,
    )
    assert response.status_code == 200
    assert (
        "This field is required."
        in response.context["medicine_form"].errors["latin_name"]
    )
    assert (
        "Select a valid choice. test is not one of the available choices."
        in response.context["medicine_form"].errors["type"]
    )


@pytest.mark.django_db
def test_logs_history(authenticated_client: Client, user: User) -> None:
    """
    Tests the logs history view.

    Checks that:
    - POST method is not allowed
    - Default view returns all logs
    - Wider range returns all logs
    - Narrower range returns a subset of logs
    - Older range returns no logs
    """
    # POST method not allowed
    response = authenticated_client.post("/dashboard/logs-history/")
    assert response.status_code == 405

    end_date = date.today()
    for i in range(1, 11):
        DayLog.objects.create(date=end_date - timedelta(days=i), strength=10, user=user)

    # Default view - should return all logs
    response = authenticated_client.get("/dashboard/logs-history/")
    assert response.status_code == 200
    assert response.context["day_logs"].count() == 10

    # Wider range should return all logs
    response = authenticated_client.get(
        "/dashboard/logs-history/?dateFrom=2023-01-01&dateTo=2050-01-01"
    )
    assert response.context["day_logs"].count() == 10

    # Narrower range should return 5 logs
    five_days_ago = end_date - timedelta(days=5)
    response = authenticated_client.get(
        f"/dashboard/logs-history/?dateFrom={five_days_ago.isoformat()}&dateTo={end_date.isoformat()}"
    )
    assert response.context["day_logs"].count() == 5

    # Older range should return 0 logs
    sixty_days_ago = end_date - timedelta(days=60)
    thirty_days_ago = end_date - timedelta(days=30)
    response = authenticated_client.get(
        f"/dashboard/logs-history/?dateTo={thirty_days_ago.isoformat()}&dateFrom={sixty_days_ago.isoformat()}"
    )
    assert response.context["day_logs"].count() == 0


@pytest.mark.django_db
def test_export_report_view(authenticated_client: Client, user: User) -> None:
    # POST method not allowed
    response = authenticated_client.post("/dashboard/export-report/")
    assert response.status_code == 405

    end_date = date.today()
    for i in range(1, 11):
        DayLog.objects.create(date=end_date - timedelta(days=i), strength=10, user=user)

    # Default view - should return all logs
    response = authenticated_client.get("/dashboard/export-report/")
    assert response.status_code == 200
    assert len(response.context["day_logs"]) == 10

    # Response should be a PDF
    assert response.headers["Content-Type"] == "application/pdf"

    # Wider range should return all logs
    response = authenticated_client.get(
        "/dashboard/export-report/?dateFrom=2023-01-01&dateTo=2050-01-01"
    )
    assert response.status_code == 200
    assert len(response.context["day_logs"]) == 10

    # Narrower range should return 5 logs
    five_days_ago = end_date - timedelta(days=5)
    response = authenticated_client.get(
        f"/dashboard/export-report/?dateFrom={five_days_ago.isoformat()}&dateTo={end_date.isoformat()}"
    )
    assert response.status_code == 200
    assert len(response.context["day_logs"]) == 5

    # Older range should return 0 logs
    sixty_days_ago = end_date - timedelta(days=60)
    thirty_days_ago = end_date - timedelta(days=30)
    response = authenticated_client.get(
        f"/dashboard/export-report/?dateTo={thirty_days_ago.isoformat()}&dateFrom={sixty_days_ago.isoformat()}"
    )
    assert response.status_code == 200
    assert len(response.context["day_logs"]) == 0


@pytest.mark.django_db
def test_visits_view(authenticated_client: Client, user: User) -> None:
    for i in range(1, 6):
        # Past visits
        Visit.objects.create(date=date.today() - timedelta(days=i), user=user)
        # Future visits
        Visit.objects.create(date=date.today() + timedelta(days=i), user=user)

    # Default view - should return all views
    response = authenticated_client.get("/dashboard/visits/")
    assert response.status_code == 200
    assert response.context["visits"].count() == 10
    assert response.context["next_visit"] is not None
    assert response.context["days_to_next_visit"] == 1

    # Wider range should return all views
    response = authenticated_client.get(
        "/dashboard/visits/?dateFrom=2023-01-01&dateTo=2050-01-01"
    )
    assert response.context["visits"].count() == 10
    assert response.context["next_visit"] is not None
    assert response.context["days_to_next_visit"] == 1

    # Narrower range should return 5 views
    five_days_ago = date.today() - timedelta(days=5)
    response = authenticated_client.get(
        f"/dashboard/visits/?dateFrom={five_days_ago.isoformat()}&dateTo={date.today().isoformat()}"
    )
    assert response.context["visits"].count() == 5

    # Older range should return 0 views
    sixty_days_ago = date.today() - timedelta(days=60)
    thirty_days_ago = date.today() - timedelta(days=30)
    response = authenticated_client.get(
        f"/dashboard/visits/?dateTo={thirty_days_ago.isoformat()}&dateFrom={sixty_days_ago.isoformat()}"
    )
    assert response.context["visits"].count() == 0
    assert response.context["next_visit"] is not None
    assert response.context["days_to_next_visit"] == 1


@pytest.mark.django_db
def test_visits_view_create(authenticated_client: Client, user: User) -> None:
    req_date = date.today().isoformat()
    payload = {
        "date": req_date,
        "specialist": "test",
    }
    response = authenticated_client.post(
        "/dashboard/visits/", payload, headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert response.__class__.__name__ == "HttpResponseClientRedirect"
    assert response.headers["HX-Redirect"] == "/dashboard/visits/"
    assert Visit.objects.filter(date=req_date, specialist="test").count() == 1


@pytest.mark.django_db
def test_visit_view_without_next_visit(
    authenticated_client: Client, user: User
) -> None:
    Visit.objects.create(date=date.today() - timedelta(days=5), user=user)
    response = authenticated_client.get("/dashboard/visits/")
    assert response.status_code == 200
    assert response.context["visits"].count() == 1
    assert response.context["next_visit"] is None
    assert response.context["days_to_next_visit"] is None


@pytest.mark.django_db
def test_delete_visit_view(authenticated_client: Client, user: User) -> None:
    visit = Visit.objects.create(date=date.today() - timedelta(days=5), user=user)
    response = authenticated_client.delete(f"/dashboard/visits/{visit.id}/")
    assert response.status_code == 200

    response = authenticated_client.delete(f"/dashboard/visits/{visit.id}/")
    assert response.status_code == 404

    # Visit should be deleted
    assert Visit.objects.filter(id=visit.id).count() == 0

    # Visit from the other user should not be deleted
    other_user = User.objects.create_user(
        email="other_user@test.com", password="password"
    )
    new_visit = Visit.objects.create(
        date=date.today() - timedelta(days=5), user=other_user
    )
    response = authenticated_client.delete(f"/dashboard/visits/{new_visit.id}/")
    assert response.status_code == 403

    # Post method not allowed
    response = authenticated_client.post(f"/dashboard/visits/{new_visit.id}/")
    assert response.status_code == 405

    # Get method not allowed
    response = authenticated_client.get(f"/dashboard/visits/{new_visit.id}/")
    assert response.status_code == 405
