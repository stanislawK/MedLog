from datetime import date, timedelta
from typing import Any

import pytest
from core.models.user import User
from core.models.visit import Visit


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param(
            {
                "date": date.today() - timedelta(days=10),
            },
            {
                "date": date.today() - timedelta(days=10),
                "planned": False,
            },
            id="Date in the past",
        ),
        pytest.param(
            {
                "date": date.today() + timedelta(days=10),
            },
            {
                "date": date.today() + timedelta(days=10),
                "planned": True,
            },
            id="Date in the future",
        ),
        pytest.param(
            {"date": date.today() + timedelta(days=10), "specialist": "test"},
            {
                "date": date.today() + timedelta(days=10),
                "planned": True,
                "specialist": "test",
            },
            id="With specialist",
        ),
        pytest.param(
            {
                "date": date.today() - timedelta(days=10),
                "planned": True,
            },
            {
                "date": date.today() - timedelta(days=10),
                "planned": True,
            },
            id="Override planned to True",
        ),
        pytest.param(
            {
                "date": date.today() + timedelta(days=10),
                "planned": False,
            },
            {
                "date": date.today() + timedelta(days=10),
                "planned": False,
            },
            id="Override planned to False",
        ),
    ],
)
@pytest.mark.django_db
def test_visit_model(test_input: dict[str, Any], expected: dict[str, Any], user: User):
    visit = Visit.objects.create(user=user, **test_input)
    for attr, value in expected.items():
        assert getattr(visit, attr) == value
    assert visit.user == user
