import json
from pathlib import Path

from django.http import HttpRequest
from django.shortcuts import render
import folium

from .models import Location


with open(Path(__file__).parent.parent.absolute() / 'travel' / 'yosemite.geo.json') as f:
    YOSEMITE_MAP = json.load(f)
YOSEMITE_MAP = YOSEMITE_MAP['features'][0]['geometry']['coordinates'][0]
CIRCLE_RADIUS = 7
COLOR = 'red'


def propose(request):
    return render(request, 'locations/propose.html')


def all_points_map(request: HttpRequest):
    m = folium.Map(location=[37.85, -119.55], 
                   zoom_start=10,
                   tiles='Stamen Terrain')

    locations = Location.objects.all()

    for location in locations:
        folium.CircleMarker(location=[location.latitude, location.longitude],
                            radius=CIRCLE_RADIUS,
                            tooltip=location.name,
                            color=COLOR,
                            fill=True,
                            fill_color=COLOR
                            ).add_to(m)
    folium.PolyLine(YOSEMITE_MAP, color='blue').add_to(m)

    context = {'map': m._repr_html_()}

    return render(request, 'locations/all_points_map.html', context)
