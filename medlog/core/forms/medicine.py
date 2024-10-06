from django import forms


class MedicineForm(forms.Form):
    marketing_name = forms.CharField(
        label="Marketing Name", max_length=100, required=True
    )
    latin_name = forms.CharField(label="Latin Name", max_length=100, required=True)
    dose = forms.IntegerField(label="Dose", required=True)
