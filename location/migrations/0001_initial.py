# Generated by Django 2.2.6 on 2019-10-16 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True)),
                ('last_edited_date', models.DateField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('kind', models.CharField(choices=[('p', 'PEEK'), ('v', 'VALLEY'), ('rvr', 'RIVER'), ('lk', 'LAKE'), ('rdg', 'RIDGE'), ('th', 'TRAIL_HEAD'), ('m', 'MEADOW'), ('o', 'OTHER'), ('cg', 'CAMPGROUND'), ('b', 'BASIN'), ('a', 'AREA')], max_length=3)),
                ('is_in_park', models.BooleanField()),
                ('note', models.TextField()),
            ],
        ),
    ]
