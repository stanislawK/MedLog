from datetime import date

from django.db import models


class Visit(models.Model):
    class Meta:
        db_table = "Visits"
        ordering = ["-date"]

    date = models.DateField()
    planned = models.BooleanField()
    specialist = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="visits")

    def save(self, **kwargs):
        if self.planned is None and self.date >= date.today():
            self.planned = True
        elif self.planned is None:
            self.planned = False
        super().save(**kwargs)

    def __str__(self):
        return self.date.isoformat()
