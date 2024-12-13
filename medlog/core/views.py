from datetime import date, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django_htmx.http import HttpResponseClientRedirect

from core.forms import LogEntryForm, LoginForm, MedicineForm
from core.models import Medicine
from core.utils import HtmxHttpRequest, parse_day_log_form


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
    context["show_medicine_modal"] = request.GET.get("medicineModal", "false") == "true"
    context["medicine_type"] = request.GET.get("medType", "acute")
    if context["show_medicine_modal"]:
        context["medicine_form"] = MedicineForm()
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
        requested_date = parse_day_log_form(request)
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
@login_required
def logs_history_view(request: HtmxHttpRequest) -> HttpResponse:
    context = dict()
    if start_date := request.GET.get("dateFrom"):
        try:
            start_date = date.fromisoformat(start_date)
        except ValueError:
            start_date = date.today() - timedelta(days=30)
    else:
        start_date = date.today() - timedelta(days=30)

    if end_date := request.GET.get("dateTo"):
        try:
            end_date = date.fromisoformat(end_date)
        except ValueError:
            end_date = date.today()
    else:
        end_date = date.today()

    context["start_date"] = str(start_date.isoformat())
    context["end_date"] = end_date.isoformat()
    context["day_logs"] = request.user.day_logs.filter(
        date__gte=start_date, date__lte=end_date
    )
    return render(request, "dashboard/components/logList.html", context=context)


@require_GET
@login_required
def logs_stats_view(request: HtmxHttpRequest) -> HttpResponse:
    return logs_history_view(request)


@require_GET
@login_required
def visits_view(request: HtmxHttpRequest) -> HttpResponse:
    return logs_history_view(request)


@require_GET
def logout_view(request: HtmxHttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/")


@require_POST
@login_required
def add_medicine_view(request: HtmxHttpRequest) -> HttpResponse:
    form = MedicineForm(request.POST)
    if form.is_valid():
        Medicine.objects.create(**form.cleaned_data)
        return HttpResponseClientRedirect("/dashboard")
    return render(
        request, "dashboard/components/addMedicineForm.html", {"medicine_form": form}
    )
