from django import forms
from django.utils.translation import gettext_lazy as _


class MedicineForm(forms.Form):
    marketing_name = forms.CharField(
        label=_("Marketing Name"), max_length=100, required=True
    )
    latin_name = forms.CharField(label=_("Latin Name"), max_length=100, required=True)
    dose = forms.IntegerField(label=_("Dose"), required=True)
    type = forms.ChoiceField(
        label="Type", choices=[("preventive", "Preventive"), ("acute", "Acute")]
    )
    dose_unit = forms.CharField(label="Dose Unit", max_length=100, initial="mg")
