# Generated by Django 2.2.6 on 2019-10-18 23:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0020_auto_20191018_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travel',
            name='contacts',
            field=models.ManyToManyField(related_name='contacts', to=settings.AUTH_USER_MODEL),
        ),
    ]