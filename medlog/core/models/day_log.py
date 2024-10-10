from django.db import models


class DayLog(models.Model):
    class Meta:
        db_table = "DayLogs"
        ordering = ["-date"]

    strength = models.IntegerField()
    date = models.DateField()
    notes = models.CharField(max_length=255, null=True, blank=True)
    medicines = models.ManyToManyField("Medicine", related_name="day_logs", blank=True)
    hr_records = models.ManyToManyField("HrRecord", related_name="day_logs", blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="day_logs")

    def __str__(self):
        return self.date.strftime("%d-%m-%Y")
