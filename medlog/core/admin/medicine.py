from django.contrib import admin

from core.models import Medicine


class MedicineAdmin(admin.ModelAdmin):
    list_display = ("latin_name", "marketing_name", "dose", "dose_unit", "type")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "dose_unit":
            formfield.initial = "mg"
            formfield.disabled = True
        return formfield


admin.site.register(Medicine, MedicineAdmin)
