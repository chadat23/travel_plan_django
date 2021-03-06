import datetime

from django.db import models
from django.contrib.auth.models import User

from colors.models import Color
from locations.models import Location
from users.models import Profile
from vehicles.models import Vehicle


class Travel(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)
    last_edited_date: datetime = models.DateField(auto_now=True)

    start_date: datetime = models.DateField(null=True, blank=True)
    entry_point: Location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,
                                              related_name='entry_point', null=True, blank=True)
    end_date: datetime = models.DateField(null=True, blank=True)
    exit_point: Location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, null=True, blank=True)

    tracked: bool = models.BooleanField(null=True, blank=True)
    plb: str = models.CharField(max_length=20, null=True, blank=True)

    trip_leader: User = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)

    vehicle: Vehicle = models.ForeignKey(Vehicle, on_delete=models.DO_NOTHING, null=True, blank=True)
    vehicle_location = models.CharField(max_length=50, null=True, blank=True)

    bivy_gear: bool = models.BooleanField(null=True, blank=True)
    compass: bool = models.BooleanField(null=True, blank=True)
    first_aid_kit: bool = models.BooleanField(null=True, blank=True)
    flagging: bool = models.BooleanField(null=True, blank=True)
    flare: bool = models.BooleanField(null=True, blank=True)
    flashlight: bool = models.BooleanField(null=True, blank=True)
    gps: bool = models.BooleanField(null=True, blank=True)
    head_lamp: bool = models.BooleanField(null=True, blank=True)
    helmet: bool = models.BooleanField(null=True, blank=True)
    ice_axe: bool = models.BooleanField(null=True, blank=True)
    map: bool = models.BooleanField(null=True, blank=True)
    matches: bool = models.BooleanField(null=True, blank=True)
    probe_pole: bool = models.BooleanField(null=True, blank=True)
    radio: bool = models.BooleanField(null=True, blank=True)
    rope: bool = models.BooleanField(null=True, blank=True)
    shovel: bool = models.BooleanField(null=True, blank=True)
    signal_mirror: bool = models.BooleanField(null=True, blank=True)
    space_blanket: bool = models.BooleanField(null=True, blank=True)
    spare_battery: bool = models.BooleanField(null=True, blank=True)
    tent: bool = models.BooleanField(null=True, blank=True)
    whistle: bool = models.BooleanField(null=True, blank=True)

    days_of_food: float = models.FloatField(null=True, blank=True)
    weapon: str = models.CharField(max_length=50, null=True, blank=True)
    radio_monitor_time: str = models.CharField(max_length=20, null=True, blank=True)
    off_trail_travel: bool = models.BooleanField(null=True, blank=True)
    cell_number: str = models.CharField(max_length=20, null=True, blank=True)
    satellite_number: str = models.CharField(max_length=20, null=True, blank=True)

    contacts = models.ManyToManyField(User, related_name='contacts')

    gar_average: int = models.IntegerField(null=True, blank=True)
    gar_mitigated: int = models.IntegerField(null=True, blank=True)
    gar_mitigations: str = models.TextField(null=True, blank=True)
    notes: str = models.TextField(null=True, blank=True)

    submitted: bool = models.BooleanField(null=True, blank=True, default=False)


class TravelUserUnit(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)

    traveler: User = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    travel: Travel = models.ForeignKey(Travel, on_delete=models.DO_NOTHING, null=True, blank=True)

    pack_color: Color = models.ForeignKey(Color, on_delete=models.DO_NOTHING,
                                          related_name='pack_color', null=True, blank=True)
    tent_color: Color = models.ForeignKey(Color, on_delete=models.DO_NOTHING,
                                          related_name='tent_color', null=True, blank=True)
    fly_color: Color = models.ForeignKey(Color, on_delete=models.DO_NOTHING,
                                         related_name='fly_color', null=True, blank=True)

    supervision: int = models.IntegerField(null= True, blank=True)
    planning: int = models.IntegerField(null= True, blank=True)
    contingency: int = models.IntegerField(null= True, blank=True)
    comms: int = models.IntegerField(null= True, blank=True)
    team_selection: int = models.IntegerField(null= True, blank=True)
    fitness: int = models.IntegerField(null= True, blank=True)
    env: int = models.IntegerField(null= True, blank=True)
    complexity: int = models.IntegerField(null= True, blank=True)

    def total_gar_score(self):
        return (self.supervision + self.planning + self.contingency + self.comms 
                + self.team_selection + self.fitness + self.env + self.complexity)

    def __str__(self):
        return f'{self.created_date.strftime("%Y-%m-%d")} {self.traveler.profile.name}, ' \
               f'{self.travel.entry_point.name} - {self.travel.entry_point.name}'


class TravelDayPlan(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)

    date: datetime = models.DateField(null=True, blank=True)
    starting_point: Location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,
                                                 related_name='starting_point', null=True, blank=True)
    ending_point: Location = models.ForeignKey(Location, on_delete=models.DO_NOTHING,
                                               related_name='ending_point', null=True, blank=True)
    route: str = models.CharField(max_length=255, null=True, blank=True)
    mode: str = models.CharField(max_length=50, null=True, blank=True)

    travel: Travel = models.ForeignKey(Travel, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return f'{str(self.date)} {self.starting_point} {self.ending_point} {self.route} {self.mode}'

    def __str__(self):
        return f'{str(self.date)} {self.starting_point} {self.ending_point} {self.route} {self.mode} {self.travel.id}'


class TravelFile(models.Model):
    created_date: datetime = models.DateTimeField(auto_now_add=True)

    file = models.FileField(null=True, blank=True, upload_to='travel_files')
    travel = models.ForeignKey(Travel, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.file.name
