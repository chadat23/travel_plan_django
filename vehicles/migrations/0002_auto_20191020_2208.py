# Generated by Django 2.2.6 on 2019-10-21 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
