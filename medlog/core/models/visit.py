from datetime import date

from django.db import models
from typing_extensions import Self

from core.models.user import User


class Visit(models.Model):
    class Meta:
        db_table = "Visits"
        ordering = ["-date"]

    date = models.DateField()
    specialist = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="visits")

    def is_planned(self: Self) -> bool:
        return self.date >= date.today()

    @classmethod
    def next_visit(cls: Self, user: "User") -> Self | None:
        """
        Get the next visit of a user.

        :param user: The user for whom to get the next visit.
        :type user: User
        :return: The next visit of the user or None if there are no upcoming visits.
        :rtype: Visit
        """
        return user.visits.filter(date__gte=date.today()).order_by("date").first()

    @classmethod
    def last_visit(cls: Self, user: "User") -> Self | None:
        """
        Get the last visit of a user.

        :param user: The user for whom to get the last visit.
        :type user: User
        :return: The last visit of the user or None if there are no past visits.
        :rtype: Visit
        """
        return user.visits.filter(date__lt=date.today()).order_by("-date").first()

    @staticmethod
    def days_to_next_visit(next_visit: Self | None) -> int | None:
        if next_visit:
            return (next_visit.date - date.today()).days

    def __str__(self):
        return self.date.isoformat()
