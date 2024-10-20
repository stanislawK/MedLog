import pytest
from core.forms import LogEntryForm
from core.models import Medicine


@pytest.mark.django_db
def test_log_entry_form(hr_record, acute, preventive) -> None:
    preventive2 = Medicine.objects.create(
        marketing_name="Aspirin2",
        latin_name="Aspirin2",
        dose=10,
        dose_unit="mg",
        type="preventive",
    )
    correct_data = {
        "date": hr_record.date,
        "strength": 10,
        "notes": "test",
        "acutes": acute.id,
        "preventives": [preventive.id, preventive2.id],
    }
    correct_form = LogEntryForm(data=correct_data)
    assert correct_form.is_valid()

    incorrect_data = {
        "date": hr_record.date,
        "strength": 10,
        "notes": "test",
        "acutes": "test",
        "preventives": [preventive.id, preventive2.id],
    }
    incorrect_form = LogEntryForm(data=incorrect_data)
    assert not incorrect_form.is_valid()
