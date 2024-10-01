from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import HttpResponseClientRedirect
from django_htmx.middleware import HtmxDetails

from core.forms import LoginForm


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
    context["hr_records"] = request.user.hr_records.all()
    return render(request, "dashboard/main.html", context=context)


@require_GET
def logout_view(request: HtmxHttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/")
