import datetime

from django.db import models
from django.contrib.auth.models import User

class Travel(models.Model):
    created_date: datetime = models.DateField(auto_now_add=True)
    last_edited_date: datetime = models.DateField(auto_now=True)

    start_date: datetime = models.DateField()

    trip_leader: User = models.ForeignKey(User, on_delete=models.CASCADE)

    plb: str = models.CharField(max_length=20)
    note: str = models.TextField()

