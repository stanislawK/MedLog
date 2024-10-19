from datetime import date, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django_htmx.http import HttpResponseClientRedirect
from django_htmx.middleware import HtmxDetails

from core.forms import LogEntryForm, LoginForm
from core.models import Medicine


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


@require_GET
def index(request: HtmxHttpRequest) -> HttpResponse:
    context = dict()
    context["show_login_modal"] = request.GET.get("loginModal", "false") == "true"
    if context["show_login_modal"]:
        context["form"] = LoginForm()
    return render(request, "home.html", context)


@require_POST
def login_view(request: HtmxHttpRequest) -> HttpResponse:
    form = LoginForm(request.POST)
    if form.is_valid():
        login(request, form.get_user())
        return HttpResponseClientRedirect("/dashboard")
    return render(request, "components/loginForm.html", {"form": form})


@require_GET
@login_required
def dashboard_main(request: HtmxHttpRequest) -> HttpResponse:
    context = dict()
    context["day_logs"] = request.user.day_logs.filter(
        date__gte=date.today() - timedelta(days=30)
    )
    return render(request, "dashboard/main.html", context=context)


@require_http_methods(["GET", "POST"])
def add_log_form(request: HtmxHttpRequest, req_date: str | None = None) -> HttpResponse:
    context = dict()
    context["available_preventives"] = Medicine.objects.filter(type="preventive")
    context["available_acutes"] = Medicine.objects.filter(type="acute")
    context["form"] = LogEntryForm()
    if req_date and request.method == "GET" and request.htmx:
        try:
            requested_date = date.fromisoformat(req_date)
        except ValueError:
            requested_date = date.today()
    elif request.method == "POST" and request.htmx:
        form = LogEntryForm(request.POST)
        if form.is_valid():
            requested_date = form.cleaned_data["date"]
            if not (
                day_log := request.user.day_logs.filter(date=requested_date).first()
            ):
                day_log = request.user.day_logs.create(date=requested_date, strength=0)
            day_log.strength = form.cleaned_data["strength"]
            day_log.notes = form.cleaned_data["notes"]
            day_log.medicines.add(*form.cleaned_data["acutes"])
            day_log.medicines.add(*form.cleaned_data["preventives"])
            day_log.save()
        else:
            requested_date = date.today()
    else:
        requested_date = date.today()
    context["current_entry"] = request.user.day_logs.filter(date=requested_date).first()
    if context["current_entry"] is None:
        context["current_entry"] = request.user.day_logs.create(
            date=requested_date, strength=0
        )
    next_day = requested_date + timedelta(days=1)
    previous_day = requested_date - timedelta(days=1)
    context["next_day"] = next_day.isoformat()
    context["previous_day"] = previous_day.isoformat()
    return render(request, "dashboard/components/addLogForm.html", context=context)


@require_GET
def logout_view(request: HtmxHttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/")
