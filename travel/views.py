from copy import deepcopy
import datetime
from datetime import datetime as dt
import json
import os
from pathlib import Path
import random
from typing import Optional, List

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
import folium

from .models import Travel, TravelUserUnit, TravelDayPlan
from colors.models import Color
from colors import services as color_services
from locations.models import Location
from travel_utils import file_utils, pdf_util, email_util
from users import services as user_services
from vehicles.models import Vehicle
from vehicles import services as vehicle_services


with open(Path(__file__).parent.absolute() / 'yosemite.geo.json') as f:
    YOSEMITE_MAP = json.load(f)
YOSEMITE_MAP = YOSEMITE_MAP['features'][0]['geometry']['coordinates'][0]
PAGINATION_COUNT = 10
CIRCLE_RADIUS = 7

def entry(request: HttpRequest):
    context = {
        'title': 'Travel Plan Entry',
        'colors': Color.objects.order_by('name').values_list('name', flat=True),
        'locations': Location.objects.order_by('name').values_list('name', flat=True),
        'names': User.objects.order_by('-profile__name').filter(profile__active=True).values_list('profile__name', flat=True),
        'vehicles': [str(v) for v in Vehicle.objects.order_by('plate').filter(active=True).all()],
        'error': '',
    }

    if request.method == 'POST':
        context = _fill_context(request, context)
        context = _fill_travelers(request, context)
        context = _fill_day_plans(request, context)
        context = _fill_contacts(request, context)

        _validate(request, context)
        if context.get('error'):
            return render(request, 'travel/entry.html', context)

        travel, files, path = _save_data(context)

        if context['submitted']:
            email_util.email_travel(travel, files, path)
            return redirect('travel-sent')
        else:
            return redirect('travel-saved')
        
    else:
        travel = {}
        if id := request.GET.get('id'):
            travel = Travel.objects.get(pk=id)
            context = _fill_context(request, context, travel)
        context = _fill_travelers(request, context, travel)
        context = _fill_day_plans(request, context, travel)
        context = _fill_contacts(request, context, travel)
    return render(request, 'travel/entry.html', context)


def search(request: HttpRequest):
    context = {}
    order_by = '-start_date'
    order = ''
    if 'tripleaderorder' in request.GET:
        order_by = 'trip_leader__profile__name'
        order = request.GET.get('tripleaderorder')
    if 'startdateorder' in request.GET:
        order_by = 'start_date'
        order = request.GET.get('startdateorder')
    if 'entrypointorder' in request.GET:
        order_by = 'entry_point__name'
        order = request.GET.get('entrypointorder')
    if 'enddateorder' in request.GET:
        order_by = 'end_date'
        order = request.GET.get('enddateorder')
    if 'exitpointorder' in request.GET:
        order_by = 'exit_point'
        order = request.GET.get('exitpointorder')
    if 'submittedorder' in request.GET:
        order_by = 'submitted'
        order = request.GET.get('submittedorder')
    if order == 'descending':
        order_by = '-' + order_by

    travels = Travel.objects.order_by(order_by)

    context['trip_leader'] = request.GET.get('tripleader', '')
    context['entry_point'] = request.GET.get('entrypoint', '')
    context['start_date'] = request.GET.get('startdate', '')
    context['exit_point'] = request.GET.get('exitpoint', '')
    context['end_date'] = request.GET.get('enddate', '')
    context['submitted'] = request.GET.get('submitted', '')
    print('context', context['submitted'])

    if context['trip_leader']:
        travels = travels.filter(trip_leader__profile__name__iexact=context['trip_leader'])
    if context['entry_point']:
        travels = travels.filter(entry_point__name__iexact=context['entry_point'])
    if context['start_date']:
        travels = travels.filter(start_date=context['start_date'])
    if context['exit_point']:
        travels = travels.filter(exit_point__name__iexact=context['exit_point'])
    if context['end_date']:
        travels = travels.filter(end_date=context['end_date'])
    if context['submitted']:
        # context['submitted'] should be 'True' if it was submitted,
        # 'False' if it wasn't, or '' if it isn't a filter term
        if context['submitted'] == 'True':
            context['submitted_yes'] = True
            submitted = True
        else:
            context['submitted_no'] = True
            submitted = False
        travels = travels.filter(submitted=submitted)

    travels = travels.all()

    paginated_travels = Paginator(travels, PAGINATION_COUNT)
    page = request.GET.get('page')
    travels = paginated_travels.get_page(page)

    locations = Location.objects.values_list('name', flat=True)

    context['travels'] = travels
    context['locations'] = locations
    return render(request, 'travel/search.html', context)


def sent(request: HttpRequest):
    return render(request, 'travel/sent.html', {})


def saved(request: HttpRequest):
    return render(request, 'travel/saved.html', {})


def date_range_itineraries_map(request: HttpRequest):
    # https://www.youtube.com/watch?v=4RnU5qKTfYY
    # start_date = request.GET.get('start-date', '').strip()
    # https://stackoverflow.com/questions/13698975/click-link-inside-leaflet-popup-and-do-javascript
    context = {}

    if request.method == 'GET':
        context['start_date'] = str(datetime.date.today())
        context['end_date'] = str(datetime.date.today())
        context['exact_date'] = ''
        context['only_submitted'] = True
    else:
        context['exact_date'] = request.POST.get('exactdate', '')
        context['only_submitted'] = request.POST.get('onlysubmitted', '')
        if context['exact_date']:
            context['start_date'] = request.POST.get('startdate', '')
            context['end_date'] = context['start_date']
        else:
            context['start_date'] = request.POST.get('startdate', '')
            context['end_date'] = request.POST.get('enddate', '')
        
    context['start_date'] = dt.strptime(context['start_date'], '%Y-%m-%d').date()
    context['end_date'] = dt.strptime(context['end_date'], '%Y-%m-%d').date()

    m = folium.Map(location=[37.85, -119.55], 
                   zoom_start=10,
                   tiles='Stamen Terrain')
                #    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                #    attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)')

    if context['exact_date']:
        am_color = '#ff0000'
        pm_color = '#0000ff'
        key_labels = ['Starting Point', 'Ending Point']
        key_colors = [am_color, pm_color]
        color_seed = 0
        date = context['start_date']

        if context['only_submitted']:
            days = TravelDayPlan.objects.filter(date=context['start_date'], 
                                                travel__submitted=True).all()
        else:
            days = TravelDayPlan.objects.filter(date=context['start_date']).all()

        for day in days:
            call_sign = day.travel.trip_leader.profile.call_sign
            name = day.travel.trip_leader.profile.name
            color_seed += 1
            line_color = _set_line_color(color_seed)
            
            am_coordinates = [day.starting_point.latitude, day.starting_point.longitude]
            pm_coordinates = [day.ending_point.latitude, day.ending_point.longitude]

            print(day.travel)
                
            folium.CircleMarker(location=am_coordinates,
                                radius=CIRCLE_RADIUS,
                                popup=_popup(name, day.travel.id),
                                tooltip=_tool_tip(call_sign, date, day.starting_point.name),
                                color=am_color,
                                fill=True,
                                fill_color=am_color
                                ).add_to(m)
            folium.CircleMarker(location=pm_coordinates,
                                radius=CIRCLE_RADIUS,
                                popup=_popup(name, day.travel.id),
                                tooltip=_tool_tip(call_sign, date, day.ending_point.name),
                                color=pm_color,
                                fill=True,
                                fill_color=pm_color
                                ).add_to(m)

            folium.PolyLine([am_coordinates, pm_coordinates], 
                            color=line_color,
                            popup=_popup(name, day.travel.id)
                            ).add_to(m)
                    
    else:
        color_seed = 0
        key_labels = []
        key_colors = []

        if context['only_submitted']:
            travels = Travel.objects.filter(end_date__gte=context['start_date'], 
                                            start_date__lte=context['end_date'],
                                            submitted=True).select_related()
        else:
            travels = Travel.objects.filter(end_date__gte=context['start_date'], 
                                            start_date__lte=context['end_date']).select_related()

        if travels:
            first_travel_day = sorted([t.start_date for t in travels])[0]
            last_travel_day = sorted([t.end_date for t in travels])[-1]

        for travel in travels:
            m, color_seed, key_labels, key_colors = _map_travel(travel, 
                                                                m, 
                                                                first_travel_day, 
                                                                last_travel_day, 
                                                                color_seed, 
                                                                key_labels, 
                                                                key_colors)

    folium.PolyLine(YOSEMITE_MAP, color='blue').add_to(m)
    context['map'] = m._repr_html_()
    context['key'] = zip(key_labels, key_colors)

    return render(request, 'travel/date_range_itineraries_map.html', context)


def itinerary_map(request: HttpRequest):
    m = folium.Map(location=[37.85, -119.55], 
                   zoom_start=10,
                   tiles='Stamen Terrain')

    travel_id = request.GET.get('travel_id')

    travel = Travel.objects.get(pk=travel_id)
    first_travel_day = travel.start_date
    last_travel_day = travel.end_date
    m, _, key_labels, key_colors = _map_travel(travel, m, first_travel_day, last_travel_day)
    folium.PolyLine(YOSEMITE_MAP, 
                    color='blue', 
                    popup=_popup(travel.trip_leader.profile.name, travel.id)
                    ).add_to(m)

    context = {'map': m._repr_html_(), 'key': zip(key_labels, key_colors)}

    return render(request, 'travel/itinerary_map.html', context)


def _map_travel(travel: Travel, m: folium.Map, first_travel_day, last_travel_day, color_seed: int = 0, key_labels=[], key_colors=[]):

    call_sign = travel.trip_leader.profile.call_sign
    name = travel.trip_leader.profile.name
    date = travel.start_date
    color = _set_color(first_travel_day, last_travel_day, date)
    color_seed += 1
    line_color = _set_line_color(color_seed)

    location = travel.traveldayplan_set.all().order_by('date')[0].starting_point
    previous_coordinates = [location.latitude, location.longitude]
    
    folium.CircleMarker(location=previous_coordinates,
                        radius=CIRCLE_RADIUS,
                        popup=_popup(name, travel.id),
                        tooltip=_tool_tip(call_sign, date, location.name),
                        color=color,
                        fill=True,
                        fill_color=color
                        ).add_to(m)

    for day in travel.traveldayplan_set.all().order_by('date'):
        coordinates = [day.ending_point.latitude, day.ending_point.longitude]
        date = day.date
        color = _set_color(first_travel_day, last_travel_day, date)
        if day.date not in key_labels:
            key_labels.append(day.date)
            key_colors.append(color)
            
        folium.CircleMarker(location=coordinates,
                            radius=CIRCLE_RADIUS,
                            popup=_popup(name, travel.id),
                            tooltip=_tool_tip(call_sign, date, day.ending_point.name),
                            color=color,
                            fill=True,
                            fill_color=color
                            ).add_to(m)

        folium.PolyLine([previous_coordinates, coordinates], 
                        color=line_color, 
                        popup=_popup(name, travel.id)
                        ).add_to(m)
        previous_coordinates = coordinates

    return m, color_seed, key_labels, key_colors


def get_traveluserunit_call_sign_and_gear(request: HttpRequest):
    if request.method == 'GET':
        name = request.GET.get('name', '').strip()
        
        traveluserunit: dict = TravelUserUnit.objects.filter(traveler__profile__name=name)\
            .order_by('-travel__start_date', '-created_date')\
            .values('traveler__profile__call_sign', 'pack_color__name', 'tent_color__name', 'fly_color__name').first()
        print(TravelUserUnit.objects.filter(traveler__profile__name=name).all())
        if traveluserunit:
            traveluserunit['call_sign'] = traveluserunit['traveler__profile__call_sign']
            traveluserunit['pack_color'] = traveluserunit['pack_color__name']
            traveluserunit['tent_color'] = traveluserunit['tent_color__name']
            traveluserunit['fly_color'] = traveluserunit['fly_color__name']
        else:
            traveluserunit = {}
    else:
        traveluserunit = {}

    return JsonResponse(traveluserunit)


def _fill_contacts(request: HttpRequest, context: dict, travel = None) -> dict:
    context['contacts'] = []
    for i in range(2):
        rp = {}
        if request.method == 'POST':
            rp['contact_name'] = request.POST.get('contactname' + str(i), '')
            rp['contact_email'] = request.POST.get('contactemail' + str(i), '')
            rp['contact_work'] = request.POST.get('contactwork' + str(i), '')
            rp['contact_home'] = request.POST.get('contacthome' + str(i), '')
            rp['contact_cell'] = request.POST.get('contactcell' + str(i), '')
        else:
            if 'id' in request.GET and i < len(travel.contacts.all()):
                if i == 0:
                    contacts = travel.contacts.all()
                rp['contact_name'] = contacts[i].profile.name
                rp['contact_email'] = contacts[i].email
                rp['contact_work'] = contacts[i].profile.work_number
                rp['contact_home'] = contacts[i].profile.home_number
                rp['contact_cell'] = contacts[i].profile.cell_number
            else:
                rp['contact_name'] = ''
                rp['contact_email'] = ''
                rp['contact_work'] = ''
                rp['contact_home'] = ''
                rp['contact_cell'] = ''
        context['contacts'].append(rp)

    return context


def _fill_day_plans(request: HttpRequest, context: dict, travel = None) -> dict:
    context['day_plans'] = []
    for i in range(9):
        p = {}
        if request.method == 'POST':
            p['date'] = request.POST.get('date' + str(i), '')
            p['starting_point'] = request.POST.get('startingpoint' + str(i), '')
            p['ending_point'] = request.POST.get('endingpoint' + str(i), '')
            p['route'] = request.POST.get('route' + str(i), '')
            p['mode'] = request.POST.get('mode' + str(i), '')
        else:
            if 'id' in request.GET and i < len(travel.traveldayplan_set.all()):
                if i == 0:
                    days = travel.traveldayplan_set.order_by('date')
                p['date'] = days[i].date.strftime('%Y-%m-%d') if days[i].date else ''
                p['starting_point'] = days[i].starting_point.name if days[i].starting_point else ''
                p['ending_point'] = days[i].ending_point.name if days[i].ending_point else ''
                p['route'] = days[i].route
                p['mode'] = days[i].mode
            else:
                p['date'] = ''
                p['starting_point'] = ''
                p['ending_point'] = ''
                p['route'] = ''
                p['mode'] = ''
        context['day_plans'].append(p)

    return context


def _fill_travelers(request: HttpRequest, context: dict, travel: Travel = None) -> dict:
    context['travelers'] = []
    for i in range(4):
        t = {}
        if request.method == 'POST':
            t['traveler_name'] = request.POST.get('travelername' + str(i), '')
            t['call_sign'] = request.POST.get('callsign' + str(i), '')
            t['pack_color'] = request.POST.get('packcolor' + str(i), '')
            t['tent_color'] = request.POST.get('tentcolor' + str(i), '')
            t['fly_color'] = request.POST.get('flycolor' + str(i), '')
            t['supervision'] = request.POST.get('supervision' + str(i), '')
            t['planning'] = request.POST.get('planning' + str(i), '')
            t['contingency'] = request.POST.get('contingency' + str(i), '')
            t['comms'] = request.POST.get('comms' + str(i), '')
            t['team_selection'] = request.POST.get('teamselection' + str(i), '')
            t['fitness'] = request.POST.get('fitness' + str(i), '')
            t['env'] = request.POST.get('env' + str(i), '')
            t['complexity'] = request.POST.get('complexity' + str(i), '')
            t['total'] = request.POST.get('total' + str(i), '')
        else:
            if 'id' in request.GET and i < len(travel.traveluserunit_set.all()):
                if i == 0:
                    trip_leader_id = travel.trip_leader.id
                    traveluserunit = travel.traveluserunit_set.get(traveler__id=trip_leader_id)

                    travelers = travel.traveluserunit_set.all().exclude(traveler__id=trip_leader_id)
                else:
                    traveluserunit = travelers[i - 1]
                t['traveler_name'] = traveluserunit.traveler.profile.name
                t['call_sign'] = traveluserunit.traveler.profile.call_sign
                t['pack_color'] = traveluserunit.pack_color.name if traveluserunit.pack_color else ''
                t['tent_color'] = traveluserunit.tent_color.name if traveluserunit.tent_color else ''
                t['fly_color'] = traveluserunit.fly_color.name if traveluserunit.fly_color else ''
                t['supervision'] = traveluserunit.supervision
                t['planning'] = traveluserunit.planning
                t['contingency'] = traveluserunit.contingency
                t['comms'] = traveluserunit.comms
                t['team_selection'] = traveluserunit.team_selection
                t['fitness'] = traveluserunit.fitness
                t['env'] = traveluserunit.env
                t['complexity'] = traveluserunit.complexity
                t['total'] = traveluserunit.total_gar_score()
            else:
                t['traveler_name'] = ''
                t['call_sign'] = ''
                t['pack_color'] = ''
                t['tent_color'] = ''
                t['fly_color'] = ''
                t['supervision'] = ''
                t['planning'] = ''
                t['contingency'] = ''
                t['comms'] = ''
                t['team_selection'] = ''
                t['fitness'] = ''
                t['env'] = ''
                t['complexity'] = ''
                t['total'] = ''
        context['travelers'].append(t)

    return context


def _validate(request: HttpRequest, context: dict) -> dict:
    context = _validate_dates(context)

    context = _validate_fields(request, context)

    context = _validate_contacts(context)

    return context


def _validate_fields(request: HttpRequest, context: dict):
    # Validate that file uploads and off trail travel selection matches
    file_present = len(context.get('uploaded_files')) > 0
    if (context.get('off_trail_travel') and not file_present) or (not context.get('off_trail_travel') and file_present):
        context['error'] = "Either you should select that you'll be traveling off trail and select files to upload, " \
                     "or have neither of those. Sorry, there's no present way to un-select the files."

    # Validate that logical traveler/gar fields make sense
    for t in context.get('travelers'):
        if not t.get('traveler_name'):
            continue
        for k, v in t.items():
            if ('color' not in k and 'call_sign' not in k) and not v:
                context['error'] = "All values must be filled in for each travelers accompanying GAR score."
                break

    # Validate that existing locations were used
    location_fields = ['entrypoint', 'exitpoint']
    i = 0
    while request.POST.get('date' + str(i)):
        location_fields.append('startingpoint' + str(i))
        location_fields.append('endingpoint' + str(i))
        i += 1
    for field in location_fields:
        entered_name = request.POST.get(field, '')
        if not Location.objects.filter(name=entered_name).exists():
            context['error'] = "All Location fields must be set to locations that are available in the" \
                               f''' accompanying dropdown lists. "{entered_name}" isn't such a location.'''
            break

    return context


def _validate_dates(context: dict):
    if not (context.get('end_date') and context.get('start_date')
            and dt.strptime(context.get('end_date'), '%Y-%m-%d') >
            dt.strptime(context.get('start_date'), '%Y-%m-%d')):
        context['error'] = "Your exit date can't be before your entry date."

    if context.get('start_date') != context.get('day_plans')[0]['date']:
        context['error'] = "Your days' plans should start on your entry date. " \
                           "The two dates don't match. You have days that are unaccounted for."

    for plan in reversed(context.get('day_plans')):
        if plan['date'] != '':
            if context.get('end_date') != plan['date']:
                context['error'] = "Your days' plans should end on your exit date. " \
                                   "The two dates don't match. You have days that are unaccounted for."
            break

    return context


def _validate_contacts(context: dict):
    # if len(set([c['contact_name'] for c in self.contacts])) != len(self.contacts):
    #     self.error = "Duplicate responsible parties are not allowed. They all must be novel."
    #
    # if [c for c in self.contacts if not (c['contact_name'] and c['contact_email'])]:
    #     self.error = "Each Responsible Party must have a name and email."

    return context


def _fill_context(request: HttpRequest, context, travel = None) -> dict:

    if request.method == 'POST':
        if request.GET.get('id'):
            context['id'] = request.GET.get('id')
        context['start_date'] = request.POST.get('startdate')
        context['entry_point'] = request.POST.get('entrypoint')
        context['end_date'] = request.POST.get('enddate')
        context['exit_point'] = request.POST.get('exitpoint')
        context['tracked'] = request.POST.get('tracked') == 'yes'
        context['plb'] = request.POST.get('plb')

        context['vehicle_plate'] = request.POST.get('vehicleplate')
        context['vehicle_make'] = request.POST.get('vehiclemake')
        context['vehicle_model'] = request.POST.get('vehiclemodel')
        context['vehicle_color'] = request.POST.get('vehiclecolor')
        context['vehicle_location'] = request.POST.get('vehiclelocation')

        context['bivy_gear'] = request.POST.get('bivygear') == 'on'
        context['compass'] = request.POST.get('compass') == 'on'
        context['first_aid_kit'] = request.POST.get('firstaidkit') == 'on'
        context['flagging'] = request.POST.get('flagging') == 'on'
        context['flare'] = request.POST.get('flare') == 'on'
        context['flashlight'] = request.POST.get('flashlight') == 'on'
        context['gps'] = request.POST.get('gps') == 'on'
        context['head_lamp'] = request.POST.get('headlamp') == 'on'
        context['helmet'] = request.POST.get('helmet') == 'on'
        context['ice_axe'] = request.POST.get('iceaxe') == 'on'
        context['map'] = request.POST.get('map') == 'on'
        context['matches'] = request.POST.get('matches') == 'on'
        context['probe_pole'] = request.POST.get('probepole') == 'on'
        context['radio'] = request.POST.get('radio') == 'on'
        context['rope'] = request.POST.get('rope') == 'on'
        context['shovel'] = request.POST.get('shovel') == 'on'
        context['signal_mirror'] = request.POST.get('signalmirror') == 'on'
        context['space_blanket'] = request.POST.get('spaceblanket') == 'on'
        context['spare_battery'] = request.POST.get('sparebattery') == 'on'
        context['tent'] = request.POST.get('tent') == 'on'
        context['whistle'] = request.POST.get('whistle') == 'on'

        context['days_of_food'] = request.POST.get('daysoffood')
        context['weapon'] = request.POST.get('weapon')
        context['radio_monitor_time'] = request.POST.get('radiomonitortime')
        context['off_trail_travel'] = request.POST.get('offtrailtravel') == 'yes'
        context['uploaded_files'] = request.FILES.getlist('fileupload')
        context['cell_number'] = request.POST.get('cellnumber')
        context['satellite_number'] = request.POST.get('satellitenumber')

        context['gar_average'] = request.POST.get('garaverage')
        context['gar_mitigated'] = request.POST.get('garmitigated')
        context['gar_mitigations'] = request.POST.get('garmitigations')
        context['notes'] = request.POST.get('notes')

        context['submitted'] = 'submit' in request.POST

    elif 'id' in request.GET:
        context['start_date'] = travel.start_date.strftime('%Y-%m-%d')
        context['entry_point'] = travel.entry_point.name if travel.entry_point else ''
        context['end_date'] = travel.end_date.strftime('%Y-%m-%d')
        context['exit_point'] = travel.exit_point.name if travel.exit_point else ''
        context['tracked'] = travel.tracked
        context['plb'] = travel.plb

        context['vehicle_plate'] = travel.vehicle.plate if travel.vehicle else ''
        context['vehicle_make'] = travel.vehicle.make if travel.vehicle else ''
        context['vehicle_model'] = travel.vehicle.model if travel.vehicle else ''
        context['vehicle_color'] = travel.vehicle.color.name if travel.vehicle else ''
        context['vehicle_location'] = travel.vehicle_location

        context['bivy_gear'] = travel.bivy_gear
        context['compass'] = travel.compass
        context['first_aid_kit'] = travel.first_aid_kit
        context['flagging'] = travel.flagging
        context['flare'] = travel.flare
        context['flashlight'] = travel.flashlight
        context['gps'] = travel.gps
        context['head_lamp'] = travel.head_lamp
        context['helmet'] = travel.helmet
        context['ice_axe'] = travel.ice_axe
        context['map'] = travel.map
        context['matches'] = travel.matches
        context['probe_pole'] = travel.probe_pole
        context['radio'] = travel.radio
        context['rope'] = travel.rope
        context['shovel'] = travel.shovel
        context['signal_mirror'] = travel.signal_mirror
        context['space_blanket'] = travel.space_blanket
        context['spare_battery'] = travel.spare_battery
        context['tent'] = travel.tent
        context['whistle'] = travel.whistle

        context['days_of_food'] = travel.days_of_food
        context['weapon'] = travel.weapon
        context['radio_monitor_time'] = travel.radio_monitor_time
        context['off_trail_travel'] = travel.off_trail_travel
        # context['uploaded_files'] = travel.uploaded_files
        context['cell_number'] = travel.cell_number
        context['satellite_number'] = travel.satellite_number

        context['gar_average'] = travel.gar_average
        context['gar_mitigated'] = travel.gar_mitigated
        context['gar_mitigations'] = travel.gar_mitigations
        context['notes'] = travel.notes

        context['submitted'] = travel.submitted

    return context


def _save_data(context: dict):
    if 'id' in context:
        travel = Travel.objects.get(pk=context['id'])
    else:
        travel = Travel()
    travel.start_date = dt.strptime(context.get('start_date'), '%Y-%m-%d').date()
    travel.entry_point = Location.objects.filter(name=context.get('entry_point')).first()
    travel.end_date = dt.strptime(context.get('end_date'), '%Y-%m-%d').date()
    travel.exit_point = Location.objects.filter(name=context.get('exit_point')).first()
    travel.tracked = context.get('tracked')
    travel.plb = context.get('plb')
    print(context.get('travelers')[0]['traveler_name'])
    user = user_services.add_if_not_present(name=context.get('travelers')[0]['traveler_name'])
    
    travel.trip_leader = User.objects.filter(username=user.username).first()

    travel.vehicle = vehicle_services.add_if_not_present(context.get('vehicle_plate').split(' ')[0],
                                                         context.get('vehicle_make'), context.get('vehicle_model'),
                                                         context.get('vehicle_color'), active=False)
    travel.vehicle_location = context.get('vehicle_location')

    travel.bivy_gear = context.get('bivy_gear')
    travel.compass = context.get('compass')
    travel.first_aid_kit = context.get('first_aid_kit')
    travel.flagging = context.get('flagging')
    travel.flare = context.get('flare')
    travel.flashlight = context.get('flashlight')
    travel.gps = context.get('gps')
    travel.head_lamp = context.get('head_lamp')
    travel.helmet = context.get('helmet')
    travel.ice_axe = context.get('ice_axe')
    travel.map = context.get('map')
    travel.matches = context.get('matches')
    travel.probe_pole = context.get('probe_pole')
    travel.radio = context.get('radio')
    travel.rope = context.get('rope')
    travel.shovel = context.get('shovel')
    travel.signal_mirror = context.get('signal_mirror')
    travel.space_blanket = context.get('space_blanket')
    travel.spare_battery = context.get('spare_battery')
    travel.tent = context.get('tent')
    travel.whistle = context.get('whistle')

    travel.days_of_food = _optional_float(context.get('days_of_food'))
    travel.weapon = context.get('weapon')
    travel.radio_monitor_time = context.get('radio_monitor_time')
    travel.off_trail_travel = context.get('off_trail_travel')
    travel.cell_number = context.get('cell_number')
    travel.satellite_number = context.get('satellite_number')

    travel.gar_average = _optional_int(context.get('gar_average'))
    travel.gar_mitigated = _optional_int(context.get('gar_mitigated'))
    travel.gar_mitigations = context.get('gar_mitigations')
    travel.notes = context.get('notes')

    travel.submitted = context.get('submitted')

    travel.save()

    for t in context['travelers']:
        if not t.get('traveler_name'):
            break
        # user = user_services.add_if_not_present(username=t.get('traveler_name'))
        user, created = User.objects.get_or_create(username=t.get('traveler_name').strip().replace(' ', '_'))
        user_services.save_profile(user, t.get('call_sign'), None, None, None, None, None)        

        travel_user_unit = TravelUserUnit.objects.filter(travel=travel, traveler=user).first()
        if not travel_user_unit:
            travel_user_unit = TravelUserUnit()
            travel_user_unit.traveler = user
            travel_user_unit.travel = travel

        color = t.get('pack_color', '').lower().strip().title()
        if color:
            color, created = Color.objects.get_or_create(name=color)
            travel_user_unit.pack_color = color
        color = t.get('tent_color', '').lower().strip().title()
        if color:
            color, created = Color.objects.get_or_create(name=color)
            travel_user_unit.tent_color = color
        color = t.get('fly_color', '').lower().strip().title()
        if color:
            color, created = Color.objects.get_or_create(name=color)
            travel_user_unit.fly_color = color

        travel_user_unit.supervision = _optional_int(t.get('supervision'))
        travel_user_unit.planning = _optional_int(t.get('planning'))
        travel_user_unit.contingency = _optional_int(t.get('contingency'))
        travel_user_unit.comms = _optional_int(t.get('comms'))
        travel_user_unit.team_selection = _optional_int(t.get('team_selection'))
        travel_user_unit.fitness = _optional_int(t.get('fitness'))
        travel_user_unit.env = _optional_int(t.get('env'))
        travel_user_unit.complexity = _optional_int(t.get('complexity'))

        travel_user_unit.save()

    # Remove travelers who have been removed from the itinerary when edited
    traveler_names = [t.get('traveler_name') for t in context['travelers']]
    for traveler_name in TravelUserUnit.objects.filter(travel=travel).values_list('traveler__profile__name', flat=True):
        if traveler_name not in traveler_names:
            travel_user_unit = TravelUserUnit.objects.filter(travel=travel, traveler__profile__name=traveler_name)
            travel_user_unit.delete()


    # Remove day plans and then replace them to know that they're right after updating
    TravelDayPlan.objects.filter(travel=travel).delete()
    for d in context['day_plans']:
        if not d.get('date'):
            break
        day_plan = TravelDayPlan()
        day_plan.travel = travel
        day_plan.date = dt.strptime(d.get('date'), '%Y-%m-%d')
        day_plan.starting_point = Location.objects.filter(name=d.get('starting_point')).first()
        day_plan.ending_point = Location.objects.filter(name=d.get('ending_point')).first()
        day_plan.route = d.get('route') if d.get('route') else None
        day_plan.mode = d.get('mode') if d.get('mode') else None

        day_plan.save()

    travel.contacts.clear()
    for rp in context['contacts']:
        if not rp.get('contact_name'):
            break
        contact = user_services.add_if_not_present(rp.get('contact_name'), rp.get('contact_email'))
        user_services.save_profile(contact, None,
                                   rp.get('contact_work'),
                                   rp.get('contact_home'),
                                   rp.get('contact_cell'),
                                   None, None)
        travel.contacts.add(contact)

    travel.save()

    travel = Travel.objects.get(id=travel.id)
    base_name = file_utils.generate_name(travel.trip_leader.profile.name, travel.start_date.strftime('%Y%m%d'))
    path = os.path.join(settings.MEDIA_ROOT, 'travel_files')
    files = [base_name + '.pdf']
    pdf_util.make_and_save_pdf(travel, base_name, path)
    if context['uploaded_files']:
        files += file_utils.save_files_with_attributes(base_name, context['uploaded_files'], path)

    return travel, files, path


def _optional_int(numb: str) -> Optional[int]:
    if not numb:
        return
    try:
        return int(numb)
    except:
        return


def _optional_float(numb: str) -> Optional[int]:
    if not numb:
        return
    try:
        return float(numb)
    except:
        return

def _set_color(start_date, end_date, date):
    n_days = end_date - start_date #+ datetime.timedelta(days=1)
    day_number = date - start_date
    green_day = n_days / 2
    
    if day_number < green_day:
        r = int(255 * (green_day - day_number) / green_day)
        b = 0
    elif day_number > green_day:
        r = 0
        b = int(255 * (day_number - green_day) / green_day)
    else:
        r = 0
        b = 0
    g = int(255 * (1 - abs(green_day - day_number) / green_day))

    return f"#{hex(r)[2:].zfill(2)}{hex(g)[2:].zfill(2)}{hex(b)[2:].zfill(2)}"


def _set_line_color(color_seed):
    random.seed(color_seed)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    return f"#{hex(r)[2:].zfill(2)}{hex(g)[2:].zfill(2)}{hex(b)[2:].zfill(2)}"


def _tool_tip(call_sign, date, location):
    return f"<p>{call_sign}<br/>{date}<br/>{location}</>"


def _popup(name, travel_id):
    return f'<p>{name}<br /><a href=" /travel/entry/?id={travel_id} "target="_top">Plan</a></p>'
    # return f"<p>{name}<br /><a href='https://www.google.com'>Itinerary</a></p>"
    # return f"<p>{name}<br /><a href='/travel/entry/?id=7'>Itinerary</a></p>"
