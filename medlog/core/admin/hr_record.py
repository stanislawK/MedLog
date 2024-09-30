from django.contrib import admin

from core.models import HrRecord


class HrRecordAdmin(admin.ModelAdmin):
    list_display = ("systolic", "diastolic", "hr", "date", "user")
    list_filter = ("user", "date")
    search_fields = ("systolic", "diastolic", "hr", "user__username")
    ordering = ["-date"]


admin.site.register(HrRecord, HrRecordAdmin)
