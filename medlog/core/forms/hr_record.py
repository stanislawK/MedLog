from django import forms



class HrRecordForm(forms.Form):
    systolic = forms.IntegerField()
    diastolic = forms.IntegerField()
    hr = forms.IntegerField()
