import pytest
from core.forms import LogEntryForm, MedicineForm, VisitForm
from core.models import Medicine
from django.http import QueryDict


@pytest.mark.django_db
def test_log_entry_form(hr_record, acute, preventive) -> None:
    preventive2 = Medicine.objects.create(
        marketing_name="Aspirin2",
        latin_name="Aspirin2",
        dose=10,
        dose_unit="mg",
        type="preventive",
    )

    raw_correct_data = f"date=2023-10-20&strength=10&notes=test&acutes={acute.id}&preventives={preventive.id}&preventives={preventive2.id}"
    correct_form = LogEntryForm(data=QueryDict(raw_correct_data))
    assert correct_form.is_valid()

    raw_incorrect_data = f"date=2023-10-20&strength=10&notes=test&acutes=test&preventives={preventive.id}&preventives={preventive2.id}"
    incorrect_form = LogEntryForm(data=QueryDict(raw_incorrect_data))
    assert not incorrect_form.is_valid()


def test_medicine_form() -> None:
    raw_correct_data = (
        "marketing_name=test&latin_name=test&dose=10&dose_unit=mg&type=preventive"
    )
    correct_form = MedicineForm(data=QueryDict(raw_correct_data))
    assert correct_form.is_valid()

    raw_correct_data_without_unit = (
        "marketing_name=test&latin_name=test&dose=10&type=acute"
    )
    correct_form = MedicineForm(data=QueryDict(raw_correct_data_without_unit))
    assert correct_form.is_valid()
    assert correct_form.cleaned_data["dose_unit"] == "mg"

    raw_incorrect_data = (
        "marketing_name=test&latin_name=test&dose=10&dose_unit=mg&type=test"
    )
    incorrect_form = MedicineForm(data=QueryDict(raw_incorrect_data))
    assert not incorrect_form.is_valid()


def test_visit_form() -> None:
    correct_form = VisitForm(data={"specialist": "test", "date": "2023-10-20"})
    assert correct_form.is_valid()

    incorrect_form = VisitForm({"specialist": "test"})
    assert not incorrect_form.is_valid()
