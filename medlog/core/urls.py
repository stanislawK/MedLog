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
    path("dashboard/visits/", views.visits_view, name="visits"),
    path(
        "dashboard/visits/<int:visit_id>/", views.delete_visit_view, name="delete_visit"
    ),
    path("dashboard/logs-history/", views.logs_history_view, name="logs_history"),
    path("dashboard/logs-stats/", views.logs_stats_view, name="logs_stats"),
    path("dashboard/export-report/", views.export_report_view, name="export_report"),
]
