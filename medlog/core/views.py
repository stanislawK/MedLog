from datetime import date, timedelta

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django_htmx.http import HttpResponseClientRedirect
from weasyprint import HTML

from core.forms import LogEntryForm, LoginForm, MedicineForm, VisitForm
from core.models import Medicine, Visit
from core.utils import (
    HtmxHttpRequest,
    chunked_list,
    is_log_history_url,
    parse_day_log_form,
)


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

    # Handling for inline editing in the list
    if request.htmx and is_log_history_url(request.htmx.current_url_abs_path):
        context["edit"] = True

    if context.get("edit") and request.method == "POST":
        return render(
            request,
            "dashboard/components/logListRow.html",
            context={"day_log": context["current_entry"]},
        )
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

    context["start_date"] = start_date.isoformat()
    context["end_date"] = end_date.isoformat()
    context["day_logs"] = request.user.day_logs.filter(
        date__gte=start_date, date__lte=end_date
    )
    return render(request, "dashboard/components/logList.html", context=context)


@require_GET
@login_required
def export_report_view(request: HtmxHttpRequest) -> FileResponse:
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

    context["start_date"] = start_date.isoformat()
    context["end_date"] = end_date.isoformat()
    all_day_logs = request.user.day_logs.filter(
        date__gte=start_date, date__lte=end_date
    )
    documents = []
    for chunk in chunked_list(all_day_logs, 31):
        str_template = render_to_string("pdfReport.html", context={"day_logs": chunk})
        documents.append(HTML(string=str_template).render())

    # If there are no logs in the range, return an empty report
    if not documents:
        str_template = render_to_string("pdfReport.html", context={"day_logs": []})
        documents.append(HTML(string=str_template).render())

    all_pages = [page for document in documents for page in document.pages]
    pdf_report = documents[0].copy(all_pages).write_pdf()
    response = HttpResponse(pdf_report, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="ml_report_{start_date.isoformat()}-{end_date.isoformat()}.pdf"'
    )
    return response


@require_GET
@login_required
def logs_stats_view(request: HtmxHttpRequest) -> HttpResponse:
    return logs_history_view(request)


@require_http_methods(["GET", "POST"])
@login_required
def visits_view(request: HtmxHttpRequest) -> HttpResponse:
    context = dict()

    # Add visit
    if request.method == "POST" and request.htmx:
        form = VisitForm(request.POST)
        if form.is_valid():
            Visit.objects.create(user=request.user, **form.cleaned_data)
            return HttpResponseClientRedirect("/dashboard/visits/")
        else:
            context["show_visit_modal"] = True
            context["form"] = form

    # Display modal with visit form
    elif request.GET.get("newVisitModal", "false") == "true":
        context["show_visit_modal"] = True
        context["form"] = VisitForm()

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
            end_date = date.today() + timedelta(days=90)
    else:
        end_date = date.today() + timedelta(days=90)

    context["start_date"] = start_date.isoformat()
    context["end_date"] = end_date.isoformat()
    context["visits"] = request.user.visits.filter(
        date__gte=start_date, date__lte=end_date
    )
    context["next_visit"] = Visit.next_visit(request.user)
    context["days_to_next_visit"] = Visit.days_to_next_visit(context["next_visit"])
    return render(request, "dashboard/components/visitList.html", context=context)


@require_http_methods(["DELETE"])
@login_required
def delete_visit_view(request: HtmxHttpRequest, visit_id: int) -> HttpResponse:
    visit = get_object_or_404(Visit, pk=visit_id)
    if visit.user != request.user:
        return HttpResponse(status=403)
    visit.delete()
    return HttpResponse(status=200)


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
