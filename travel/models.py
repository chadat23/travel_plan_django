import datetime

from django.db import models
from django.contrib.auth.models import User

from locations.models import Location


class Travel(models.Model):
    created_date: datetime = models.DateField(auto_now_add=True)
    last_edited_date: datetime = models.DateField(auto_now=True)

    start_date: datetime = models.DateField()
    entry_point: Location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='entry_point')
    end_date: datetime = models.DateField()
    exit_point: Location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='exit_point')

    trip_leader: User = models.ForeignKey(User, on_delete=models.CASCADE)

    plb: str = models.CharField(max_length=20, null=True, blank=True)
    note: str = models.TextField(null=True, blank=True)
