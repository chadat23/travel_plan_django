import datetime

from django.db import models


class Department(models.Model):
    created_date: datetime = models.DateField(auto_now_add=True)

    name: str = models.CharField(max_length=100)
