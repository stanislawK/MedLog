import pytest
from core.models import Medicine, User
from core.utils import is_log_history_url, parse_day_log_form, populate_hr_records
from django.test import RequestFactory

HR_DATA = (120, 70, 55)


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


@pytest.mark.django_db
def test_parse_day_log_form_with_hr_record(rf: RequestFactory, user: User) -> None:
    payload = {
        "date": "2023-10-20",
        "strength": 3,
        "preventives": [],
        "acutes": [],
        "notes": "test",
        "systolic": "120",
        "diastolic": "70",
        "hr": "55",
    }
    request = rf.post("/", data=payload, user=user)
    request.user = user
    requested_date = parse_day_log_form(request)
    assert payload["date"] == str(requested_date)
    day_log = user.day_logs.filter(date=requested_date).first()
    assert day_log.strength == 3
    assert day_log.medicines.count() == 0
    assert day_log.notes == "test"
    assert day_log.hr_records.count() == 1


@pytest.mark.django_db
def test_populate_hr_records(user: User) -> None:
    # No records
    day_log = user.day_logs.create(date="2023-10-20", strength=0)
    populate_hr_records(day_log, "2023-10-20", user.pk, *HR_DATA)
    assert day_log.hr_records.count() == 1
    hr_record = day_log.hr_records.first()
    assert hr_record.systolic == HR_DATA[0]
    assert hr_record.diastolic == HR_DATA[1]
    assert hr_record.hr == HR_DATA[2]
    assert hr_record.user == user

    # One record, same data
    populate_hr_records(day_log, "2023-10-20", user.pk, *HR_DATA)
    assert day_log.hr_records.count() == 1
    hr_record = day_log.hr_records.first()
    assert hr_record.systolic == HR_DATA[0]
    assert hr_record.diastolic == HR_DATA[1]
    assert hr_record.hr == HR_DATA[2]

    # One record, new data
    new_data = (130, 80, 60)
    populate_hr_records(day_log, "2023-10-20", user.pk, *new_data)
    assert day_log.hr_records.count() == 1
    hr_record = day_log.hr_records.first()
    assert hr_record.systolic == new_data[0]
    assert hr_record.diastolic == new_data[1]
    assert hr_record.hr == new_data[2]


def test_is_log_history_url() -> None:
    assert is_log_history_url("/dashboard/logs-history/")
    assert not is_log_history_url("/dashboard/")
    assert is_log_history_url(
        "/dashboard/logs-history/?dateFrom=2023-01-01&dateTo=2050-01-01"
    )
    assert not is_log_history_url("/dashboard/add-log/")
