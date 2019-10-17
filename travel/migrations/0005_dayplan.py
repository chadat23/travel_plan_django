# Generated by Django 2.2.6 on 2019-10-16 20:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_location_active'),
        ('travel', '0004_auto_20191016_1025'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True)),
                ('datetime', models.DateField(blank=True, null=True)),
                ('route', models.CharField(blank=True, max_length=255, null=True)),
                ('mode', models.CharField(blank=True, max_length=50, null=True)),
                ('ending_point', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ending_point', to='locations.Location')),
                ('starting_point', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='starting_point', to='locations.Location')),
            ],
        ),
    ]