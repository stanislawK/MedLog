from datetime import date
from typing import Any, Generator
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import PermissionDenied
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
    splitted = urlsplit(url)
    if splitted.netloc not in settings.ALLOWED_HOSTS:
        raise PermissionDenied
    try:
        return resolve(splitted.path).url_name == "logs_history"
    except Resolver404:
        return False


def chunked_list(list_data: list[Any], chunk_size: int) -> Generator[Any, None, None]:
    for i in range(0, len(list_data), chunk_size):
        yield list_data[i : i + chunk_size]
