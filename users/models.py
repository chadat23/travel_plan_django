from django.db import models
from django.contrib.auth.models import User

from departments.models import Department


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)

    call_sign = models.CharField(max_length=20, null=True, blank=True)

    work_number = models.CharField(max_length=20, null=True, blank=True)
    home_number = models.CharField(max_length=20, null=True, blank=True)
    cell_number = models.CharField(max_length=20, null=True, blank=True)

    department: Department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    active: bool = models.BooleanField(null=True, blank=True)

    def __repr__(self):
        return f'Profile for: {self.name}'

    def __str__(self):
        return f'Profile for: {self.name}'

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

