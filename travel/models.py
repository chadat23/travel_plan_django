import datetime

from django.db import models
from django.contrib.auth.models import User

from locations.models import Location


class Travel(models.Model):
    created_date: datetime = models.DateField(auto_now_add=True)
    last_edited_date: datetime = models.DateField(auto_now=True)

    start_date: datetime = models.DateField(null=True, blank=True)
    entry_point: Location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                              related_name='entry_point', null=True, blank=True)
    end_date: datetime = models.DateField(null=True, blank=True)
    exit_point: Location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    tracked: bool = models.BooleanField(null=True, blank=True)
    plb: str = models.CharField(max_length=20, null=True, blank=True)

    trip_leader: User = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    note: str = models.TextField(null=True, blank=True)





class DayPlan(models.Model):
    created_date: datetime = models.DateField(auto_now_add=True)

    datetime: datetime = models.DateField(null=True, blank=True)
    starting_point: Location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                                 related_name='starting_point', null=True, blank=True)
    ending_point: Location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                               related_name='ending_point', null=True, blank=True)
    route: str = models.CharField(max_length=255, null=True, blank=True)
    mode: str = models.CharField(max_length=50, null=True, blank=True)

    travel: Travel = models.ForeignKey(Travel, on_delete=models.CASCADE, null=True, blank=True)

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return f'{str(self.date)} {self.starting_point} {self.ending_point} {self.route} {self.mode}'
