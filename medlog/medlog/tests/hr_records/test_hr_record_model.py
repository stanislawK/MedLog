import pytest
from core.models import HrRecord, User


@pytest.mark.django_db()
class TestHrRecordsModelCase:
    def test_hr_record_model(self, hr_record_data: dict, user: User):
        hr_record = HrRecord.objects.create(**{**hr_record_data, "user": user})
        assert hr_record.user == user

        assert (
            str(hr_record)
            == f"{hr_record.systolic}/{hr_record.diastolic} {hr_record.hr}"
        )
