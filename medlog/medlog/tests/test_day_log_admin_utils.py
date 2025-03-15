import datetime
from csv import DictReader
from pathlib import Path

import pytest
from core.admin.day_log import populate_day_log_from_csv
from core.models.day_log import DayLog
from core.models.hr_record import HrRecord
from core.models.medicine import Medicine
from core.models.user import User

INPUT_CSV_PATH = Path("./tests/day_log_data.csv")


@pytest.mark.django_db
def test_populate_day_log_from_csv(user: User) -> None:
    with open(INPUT_CSV_PATH.absolute(), "r") as f:
        reader = DictReader(f, fieldnames=["date", "strength", "medicines", "notes"])
        next(reader)
        for row in reader:
            populate_day_log_from_csv(user, row)
    day_logs = DayLog.objects.all()
    assert day_logs.count() == 5

    expected_day_logs = [
        {
            "date": datetime.date(2021, 4, 2),
            "notes": None,
            "strength": 6,
            "user_id": user.pk,
        },
        {
            "date": datetime.date(2021, 4, 1),
            "notes": None,
            "strength": 8,
            "user_id": user.pk,
        },
        {
            "date": datetime.date(2021, 3, 3),
            "notes": None,
            "strength": 8,
            "user_id": user.pk,
        },
        {
            "date": datetime.date(2021, 3, 2),
            "notes": None,
            "strength": 0,
            "user_id": user.pk,
        },
        {
            "date": datetime.date(2021, 3, 1),
            "notes": None,
            "strength": 6,
            "user_id": user.pk,
        },
    ]
    assert [
        {k: v for k, v in day_log.items() if k != "id"} for day_log in day_logs.values()
    ] == expected_day_logs
    assert Medicine.objects.count() == 2
    first_medicine = (
        day_logs.filter(date=datetime.date(2021, 3, 3)).first().medicines.first()
    )
    assert (
        first_medicine.type,
        first_medicine.marketing_name,
        first_medicine.latin_name,
        first_medicine.dose,
    ) == ("acute", "Ibuprom Max Sprint", "Ibuprofenum", 400)
    second_medicine = (
        day_logs.filter(date=datetime.date(2021, 4, 1)).first().medicines.first()
    )
    assert (
        second_medicine.type,
        second_medicine.marketing_name,
        second_medicine.latin_name,
        second_medicine.dose,
    ) == ("acute", "Dezamigren", "Almotriptani", 12)
    hr_record = HrRecord.objects.all()
    assert hr_record.count() == 1
    assert (
        hr_record[0].systolic,
        hr_record[0].diastolic,
        hr_record[0].hr,
        hr_record[0].date,
    ) == (
        125,
        83,
        55,
        datetime.datetime(2021, 4, 2, 0, 0, tzinfo=datetime.timezone.utc),
    )
    assert (
        day_logs.filter(date=datetime.date(2021, 4, 2)).first().hr_records.first()
        == hr_record[0]
    )
