from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    work_number = models.CharField(max_length=20, null=True, blank=True)
    home_number = models.CharField(max_length=20, null=True, blank=True)
    cell_number = models.CharField(max_length=20, null=True, blank=True)

    # department

    active: bool = models.BooleanField(null=True, blank=True)

    def __repr__(self):
        return f'{self.user.username}'
