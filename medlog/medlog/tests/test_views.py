import pytest
from core.models.user import User
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
