import datetime

from django.db import models


class Color(models.Model):
    created_date: datetime = models.DateField(auto_now_add=True)

    name: str = models.CharField(max_length=100)

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return f'{self.name}'
