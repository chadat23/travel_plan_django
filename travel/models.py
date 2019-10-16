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
