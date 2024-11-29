from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("loginsubmit/", views.login_view, name="login"),
    path("dashboard/", views.dashboard_main, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/add-log/<str:req_date>/", views.add_log_form, name="add-log"),
    path("dashboard/add-log/", views.add_log_form, name="add-log"),
    path("dashboard/add-medicine/", views.add_medicine_view, name="new_medicine"),
]
