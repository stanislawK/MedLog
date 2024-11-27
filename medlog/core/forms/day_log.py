from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import Medicine


class ListField(forms.Field):
    def to_python(self, value):
        """Normalize data to a list of integers."""
        if isinstance(value, list):
            return value
        elif isinstance(value, str) and "," in value:
            return value.split(",")
        elif isinstance(value, str) or isinstance(value, int):
            return [value]
        return []

    def validate(self, value):
        """Check if value consists only of valid integers."""
        super().validate(value)
        for id in value:
            try:
                int(id)
            except (TypeError, ValueError):
                raise forms.ValidationError(_("Id has to be numeric"), code="invalid")


class LogEntryForm(forms.Form):
    strength = forms.IntegerField(min_value=0, max_value=10)
    date = forms.DateField()
    notes = forms.CharField(max_length=255, required=False, empty_value="")
    preventives = ListField(required=False)
    acutes = ListField(required=False)
    hr_records = ListField(required=False)

    def clean_preventives(self):
        preventives_raw = self.fields["preventives"].clean(
            self.data.getlist("preventives")
        )
        if isinstance(preventives_raw, list):
            return Medicine.objects.filter(pk__in=preventives_raw)
        elif isinstance(preventives_raw, str) and preventives_raw.isnumeric():
            return Medicine.objects.filter(pk=int(preventives_raw))
        return list()

    def clean_acutes(self):
        acutes_raw = self.fields["acutes"].clean(self.data.getlist("acutes"))
        if isinstance(acutes_raw, list):
            return Medicine.objects.filter(pk__in=acutes_raw)
        elif isinstance(acutes_raw, str) and acutes_raw.isnumeric():
            return Medicine.objects.filter(pk=int(acutes_raw))
        return list()

    def clean_hr_records(self) -> tuple[int, int, int] | None:
        systolic = self.data.get("systolic")
        diastolic = self.data.get("diastolic")
        hr = self.data.get("hr")
        if systolic and diastolic and hr:
            try:
                return (int(systolic), int(diastolic), int(hr))
            except ValueError:
                pass
        return None
