from django.db import models


class Medicine(models.Model):
    TYPE_CHOICES = (
        ("preventive", "Preventive"),
        ("acute", "Acute"),
    )

    class Meta:
        db_table = "Medicines"

    marketing_name = models.CharField(max_length=255, null=True, blank=True)
    latin_name = models.CharField(max_length=255)
    dose = models.IntegerField()
    dose_unit = models.CharField(max_length=64)
    type = models.CharField(max_length=64, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.latin_name} {self.dose}{self.dose_unit}"
