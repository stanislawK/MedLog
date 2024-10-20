import pytest
from core.models import Medicine, User
from core.utils import parse_day_log_form
from django.test import RequestFactory


@pytest.mark.django_db
def test_parse_day_log_form(
    rf: RequestFactory, acute: Medicine, preventive: Medicine, user: User
) -> None:
    preventive2 = Medicine.objects.create(
        marketing_name="Aspirin2",
        latin_name="Aspirin2",
        dose=10,
        dose_unit="mg",
        type="preventive",
    )
    payload = {
        "date": "2023-10-20",
        "strength": 3,
        "preventives": [preventive.id, preventive2.id],
        "acutes": acute.id,
        "notes": "test",
        "systolic": "",
        "diastolic": "",
        "hr": "",
    }
    request = rf.post("/", data=payload, user=user)
    request.user = user
    requested_date = parse_day_log_form(request)
    assert payload["date"] == str(requested_date)
    day_log = user.day_logs.filter(date=requested_date).first()
    assert day_log.strength == 3
    assert day_log.medicines.count() == 3
    assert day_log.medicines.filter(pk=acute.id).exists()
    assert day_log.medicines.filter(pk=preventive.id).exists()
    assert day_log.medicines.filter(pk=preventive2.id).exists()
    assert day_log.notes == "test"
