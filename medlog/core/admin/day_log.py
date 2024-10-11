from django.contrib import admin

from core.models import DayLog


class DayLogAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "strength",
        "user",
    )
    list_filter = ("user", "date", "strength")
    search_fields = ("strength", "user__email")
    ordering = ["-date"]


admin.site.register(DayLog, DayLogAdmin)
