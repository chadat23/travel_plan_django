import datetime
import enum

from django.db import models


class KindEnum(models.Field):

    def __init__(self, *args, **kwargs):
        super(KindEnum, self).__init__(*args, **kwargs)
        if not self.choices:
            raise AttributeError('EnumField requires `choices` attribute.')

    def db_type(self):
        return "enum(%s)" % ','.join("'%s'" % k for (k, _) in self.choices)

    PEAK = 'p'
    PASS = 'ps'
    VALLEY = 'v'
    RIVER = 'rvr'
    LAKE = 'lk'
    RIDGE = 'rdg'
    TRAIL_HEAD = 'th'
    MEADOW = 'm'
    OTHER = 'o'
    CAMPGROUND = 'cg'
    BASIN = 'b'
    AREA = 'a'
    KIND_CHOICES = (
        (PEAK, 'PEAK'),
        (PASS, 'PASS'),
        (VALLEY, 'VALLEY'),
        (RIVER, 'RIVER'),
        (LAKE, 'LAKE'),
        (RIDGE, 'RIDGE'),
        (TRAIL_HEAD, 'TRAIL_HEAD'),
        (MEADOW, 'MEADOW'),
        (OTHER, 'OTHER'),
        (CAMPGROUND, 'CAMPGROUND'),
        (BASIN, 'BASIN'),
        (AREA, 'AREA'),
    )


class Location(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)
    last_edited_date: datetime = models.DateField(auto_now=True)

    name: str = models.CharField(max_length=100)

    latitude: float = models.FloatField(null=True, blank=True)
    longitude: float = models.FloatField(null=True, blank=True)
    kind: enum.Enum = models.CharField(max_length=3, choices=KindEnum.KIND_CHOICES, null=True, blank=True)
    is_in_park: bool = models.BooleanField(null=True, blank=True)
    active: bool = models.BooleanField(null=True, blank=True)
    # aliases: int = db.relationship('Location', secondary=location_association_table,
    #                                primaryjoin=id == location_association_table.c.location_1_id,
    #                                secondaryjoin=id == location_association_table.c.location_1_id,
    #                                )
    note: str = models.TextField(null=True, blank=True)

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return f'{self.name}: {self.latitude}, {self.longitude}'

    def __str__(self):
        return f'{self.name}: {self.latitude}, {self.longitude}'
