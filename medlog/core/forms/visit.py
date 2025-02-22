from django import forms
from django.utils.translation import gettext_lazy as _


class VisitForm(forms.Form):
    date = forms.DateField(label=_("Date"))
    specialist = forms.CharField(
        label=_("Specialist"), max_length=255, required=False, empty_value=""
    )
