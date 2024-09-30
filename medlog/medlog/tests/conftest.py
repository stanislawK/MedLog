from datetime import datetime

import pytest
from core.models.user import User
from django.test import Client


@pytest.fixture(scope="module")
def super_user_data():
    return {
        "email": "JohnAdminogin@example.com",
        "password": "TestTest123",
    }


@pytest.fixture(scope="module")
def user_data():
    return {
        "email": "JohnLogin@example.com",
        "password": "TestTest123",
    }


@pytest.fixture(scope="module")
def hr_record_data():
    return {
        "systolic": 120,
        "diastolic": 80,
        "hr": 55,
        "date": datetime.now(),
    }


@pytest.fixture()
@pytest.mark.django_db
def superuser(super_user_data):
    superuser = User.objects.create_superuser(**super_user_data)
    return superuser


@pytest.fixture()
@pytest.mark.django_db
def user(user_data):
    user = User.objects.create_user(**user_data)
    user.is_active = True
    user.save()
    return user


@pytest.fixture
def authenticated_client(client: Client, user: User) -> Client:
    client.force_login(user)
    return client
