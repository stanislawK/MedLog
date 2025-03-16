from csv import DictReader
from datetime import datetime
from io import StringIO

from django import forms
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path

from core.models import DayLog, Medicine, User


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class DayLogAdmin(admin.ModelAdmin):
    change_list_template = "entities/day_log_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("import-csv/", self.import_csv)]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            content = StringIO(csv_file.read().decode("latin-1"))
            reader = DictReader(
                content, fieldnames=["date", "strength", "medicines", "notes"]
            )
            # Skip header
            next(reader)
            for row in reader:
                populate_day_log_from_csv(request.user, row)
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

    list_display = (
        "date",
        "strength",
        "user",
    )
    list_filter = ("user", "date", "strength")
    search_fields = ("strength", "user__email")
    ordering = ["-date"]


admin.site.register(DayLog, DayLogAdmin)


MEDICINE_MAPPING = {
    "ibuprofen": ("acute", "Ibuprom Max Sprint", "Ibuprofenum", 400),
    "tryptany": ("acute", "Dezamigren", "Almotriptani", 12),
    "ibuprom": ("acute", "Ibuprom Max Sprint", "Ibuprofenum", 400),
    "dezamigren": ("acute", "Dezamigren", "Almotriptani", 12),
    "ibum": ("acute", "Ibum express forte", "Ibuprofenum", 400),
}


def populate_day_log_from_csv(user: User, day_log_data: dict[str, str]) -> None:
    # Convert the date string DD-MM-YYYY to a date object
    input_date = datetime.strptime(day_log_data["date"], "%d-%m-%Y").strftime(
        "%Y-%m-%d"
    )
    if not (day_log := user.day_logs.filter(date=input_date).first()):
        day_log = user.day_logs.create(
            date=input_date, strength=day_log_data["strength"]
        )
    day_log.strength = day_log_data["strength"]
    if day_log_data["notes"] and "/" in day_log_data["notes"]:
        systolic, diastolic, hr = day_log_data["notes"].split("/")
        existing_hr_record = day_log.hr_records.first()
        if existing_hr_record:
            existing_hr_record.systolic = systolic
            existing_hr_record.diastolic = diastolic
            existing_hr_record.hr = hr
            existing_hr_record.save()
        else:
            day_log.hr_records.create(
                systolic=systolic,
                diastolic=diastolic,
                hr=hr,
                date=input_date,
                user_id=user.pk,
            )
    elif (
        day_log_data["medicines"]
        and len(day_log_data["medicines"]) > 1
        and not day_log.medicines.first()
    ):
        if medicine := MEDICINE_MAPPING.get(day_log_data["medicines"]):
            med_type, marketing_name, latin_name, dose = medicine
            medicine_db = Medicine.objects.filter(
                type=med_type,
                marketing_name=marketing_name,
                latin_name=latin_name,
                dose=dose,
            ).first()
            if not medicine_db:
                medicine_db = Medicine.objects.create(
                    type=med_type,
                    marketing_name=marketing_name,
                    latin_name=latin_name,
                    dose=dose,
                )
            day_log.medicines.add(medicine_db)
    day_log.save()
