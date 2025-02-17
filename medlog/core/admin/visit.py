from django.contrib import admin

from core.models import Visit


class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "specialist",
        "user",
    )
    list_filter = ("user", "date", "specialist")
    search_fields = ("date", "user__email")
    ordering = ["-date"]


admin.site.register(Visit, VisitAdmin)
