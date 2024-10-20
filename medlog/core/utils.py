from datetime import date

from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from core.forms import LogEntryForm


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


def parse_day_log_form(request: HtmxHttpRequest) -> date:
    form = LogEntryForm(request.POST)
    if form.is_valid():
        requested_date = form.cleaned_data["date"]
        if not (day_log := request.user.day_logs.filter(date=requested_date).first()):
            day_log = request.user.day_logs.create(date=requested_date, strength=0)
        day_log.strength = form.cleaned_data["strength"]
        day_log.notes = form.cleaned_data["notes"]
        day_log.medicines.add(*form.cleaned_data["acutes"])
        day_log.medicines.add(*form.cleaned_data["preventives"])
        day_log.save()
    else:
        requested_date = date.today()
    return requested_date
