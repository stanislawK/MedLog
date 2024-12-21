from datetime import date

from django.http import HttpRequest
from django.urls import Resolver404, resolve
from django_htmx.middleware import HtmxDetails

from core.forms import LogEntryForm
from core.models import DayLog


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
        if form.cleaned_data["hr_records"]:
            populate_hr_records(
                day_log,
                requested_date,
                request.user.pk,
                *form.cleaned_data["hr_records"],
            )
        day_log.save()
    else:
        requested_date = date.today()
    return requested_date


def populate_hr_records(
    day_log: DayLog,
    requested_date: str,
    user_id: int,
    systolic: int,
    diastolic: int,
    hr: int,
) -> None:
    existing_hr_record = day_log.hr_records.first()
    if existing_hr_record:
        existing_hr_record.systolic = systolic
        existing_hr_record.diastolic = diastolic
        existing_hr_record.hr = hr
        existing_hr_record.save()
    else:
        day_log.hr_records.create(
            systolic=systolic,
            diastolic=diastolic,
            hr=hr,
            date=requested_date,
            user_id=user_id,
        )


def is_log_history_url(url: str) -> bool:
    if "?" in url:
        url = url.split("?")[0]
    print(url)
    try:
        return resolve(url).url_name == "logs_history"
    except Resolver404:
        return False
