import datetime

from django.db import models

from colors.models import Color
from departments.models import Department


class Vehicle(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)

    plate: str = models.CharField(max_length=50)
    make: str = models.CharField(max_length=50, null=True, blank=True)
    model: str = models.CharField(max_length=50, null=True, blank=True)
    color: Color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    location: str = models.CharField(max_length=50, null=True, blank=True)
    active: str = models.BooleanField(null=True, blank=True)
    department: Department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        return f'{self.plate} {self.make} {self.model} {"" if not self.color else self.color.name} {self.location}'

    @property
    def name(self):
        return self.__str__()


class Note(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)

    note: str = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
