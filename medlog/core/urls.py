from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("loginsubmit/", views.login_view, name="login"),
    path("dashboard/", views.dashboard_main, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
]
