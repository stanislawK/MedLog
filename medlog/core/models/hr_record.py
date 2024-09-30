from django.db import models


class HrRecord(models.Model):
    class Meta:
        db_table = "HrRecords"
        ordering = ["-date"]

    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    hr = models.IntegerField()
    date = models.DateTimeField()
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="hr_records"
    )

    def __str__(self):
        return f"{self.systolic}/{self.diastolic} {self.hr}"
