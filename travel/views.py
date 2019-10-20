from copy import deepcopy
from datetime import datetime
import os
from typing import Optional, List

from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import render, redirect

from .models import Travel, TravelUserUnit, TravelDayPlan
from colors.models import Color
from colors import services as color_services
from locations.models import Location
from travel_utils import file_utils, pdf_util, email_util
from users import services as user_services
from vehicles.models import Vehicle
from vehicles import services as vehicle_services

try:
    context = {
        'title': 'Travel Plan Entry',
        'colors': Color.objects.order_by('name').values_list('name', flat=True),
        'locations': Location.objects.order_by('name').values_list('name', flat=True),
        'usernames': User.objects.order_by('-username').filter(profile__active=True).values_list('username', flat=True),
        'vehicles': [str(v) for v in Vehicle.objects.order_by('plate').filter(active=True).all()],
        'error': '',
        'start_date': '',
        'entry_point': '',
        'end_date': '',
        'exit_point': '',
        'tracked': True,
        'vehicle_plate': '',
        'vehicle_make': '',
        'vehicle_model': '',
        'vehicle_color': '',
        'vehicle_location': '',
        'off_trail_travel': True,
    }

    for i in range(4):
        context['travelername' + str(i)] = ''
        context['callsign' + str(i)] = ''
        context['packcolor' + str(i)] = ''
        context['tentcolor' + str(i)] = ''
        context['flycolor' + str(i)] = ''

    for i in range(9):
        context['date' + str(i)] = ''
        context['startingpoint' + str(i)] = ''
        context['endingpoint' + str(i)] = ''
        context['route' + str(i)] = ''
        context['mode' + str(i)] = ''

    for i in range(2):
        context['contactname' + str(i)] = ''
        context['contactemail' + str(i)] = ''
        context['contactwork' + str(i)] = ''
        context['contacthome' + str(i)] = ''
        context['contactcell' + str(i)] = ''
except:
    pass


def entry(request: HttpRequest):
    con = deepcopy(context)

    if request.method == 'POST':
        con = _fill_context(request)
        con = _fill_travelers(request, con)
        con = _fill_day_plans(request, con)
        con = _fill_contacts(request, con)

        _validate(request, con)
        if con.get('error'):
            return render(request, 'travel/entry.html', con)

        travel, files, path = _save_data(con)

        email_util.email_travel(travel, files, path)

        # return render(request, 'travel/entry.html', con)
        return redirect('travel-sent')
    else:
        con = _fill_travelers(request, con)
        con = _fill_day_plans(request, con)
        con = _fill_contacts(request, con)
    return render(request, 'travel/entry.html', con)


def search(request: HttpRequest):
    return render(request, 'travel/search.html', context)


def sent(request: HttpRequest):
    return render(request, 'travel/sent.html', {})


def _fill_contacts(request: HttpRequest, context: dict) -> dict:
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
            rp['contact_name'] = ''
            rp['contact_email'] = ''
            rp['contact_work'] = ''
            rp['contact_home'] = ''
            rp['contact_cell'] = ''
        context['contacts'].append(rp)

    return context


def _fill_day_plans(request: HttpRequest, context: dict) -> dict:
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
            p['date'] = ''
            p['starting_point'] = ''
            p['ending_point'] = ''
            p['route'] = ''
            p['mode'] = ''
        context['day_plans'].append(p)

    return context


def _fill_travelers(request: HttpRequest, context: dict) -> dict:
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
        context['travelers'].append(t)

    return context


def _validate(request: HttpRequest, context: dict) -> dict:
    context = _validate_dates(context)

    context = _validate_fields(request, context)

    context = _validate_contacts(context)

    return context


def _validate_fields(request: HttpRequest, context: dict):
    # if it's reported that there'll be off trail travel then there should be uploaded files
    # if self.uploaded_files:
    #     file_name_1 = self.uploaded_files[0].filename
    # else:
    #     file_name_1 = ''
    # if (self.off_trail_travel and (not file_name_1)) or (not self.off_trail_travel and file_name_1):
    #     self.error = "Either you should select that you'll be traveling off trail and select files to upload, " \
    #                  "or have neither of those. Sorry, there's no present way to un-select the files."

    # Validate that logical traveler/gar fields make sense
    for t in context.get('travelers'):
        if not t.get('traveler_name'):
            continue
        for k, v in t.items():
            if 'color' not in k and not v:
                context['error'] = "All fields must be filled in for each traveler and each accompanying GAR score."
                break

    return context


def _validate_dates(context: dict):
    if not (context.get('end_date') and context.get('start_date')
            and datetime.strptime(context.get('end_date'), '%Y-%m-%d') >
            datetime.strptime(context.get('start_date'), '%Y-%m-%d')):
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


def _fill_context(request: HttpRequest) -> dict:
    con = deepcopy(context)
    con['start_date'] = request.POST.get('startdate', '')
    con['entry_point'] = request.POST.get('entrypoint', '')
    con['end_date'] = request.POST.get('enddate', '')
    con['exit_point'] = request.POST.get('exitpoint', '')
    con['tracked'] = request.POST.get('tracked', '') == 'yes'
    con['plb'] = request.POST.get('plb', '')

    # con = _fill_travelers(request, con)

    con['vehicle_plate'] = request.POST.get('vehicleplate', '')
    con['vehicle_make'] = request.POST.get('vehiclemake', '')
    con['vehicle_model'] = request.POST.get('vehiclemodel', '')
    con['vehicle_color'] = request.POST.get('vehiclecolor', '')
    con['vehicle_location'] = request.POST.get('vehiclelocation', '')

    con['bivy_gear'] = request.POST.get('bivygear', '') == 'on'
    con['compass'] = request.POST.get('compass', '') == 'on'
    con['first_aid_kit'] = request.POST.get('firstaidkit', '') == 'on'
    con['flagging'] = request.POST.get('flagging', '') == 'on'
    con['flare'] = request.POST.get('flare', '') == 'on'
    con['flashlight'] = request.POST.get('flashlight', '') == 'on'
    con['gps'] = request.POST.get('gps', '') == 'on'
    con['head_lamp'] = request.POST.get('headlamp', '') == 'on'
    con['helmet'] = request.POST.get('helmet', '') == 'on'
    con['ice_axe'] = request.POST.get('iceaxe', '') == 'on'
    con['map'] = request.POST.get('map', '') == 'on'
    con['matches'] = request.POST.get('matches', '') == 'on'
    con['probe_pole'] = request.POST.get('probepole', '') == 'on'
    con['radio'] = request.POST.get('radio', '') == 'on'
    con['rope'] = request.POST.get('rope', '') == 'on'
    con['shovel'] = request.POST.get('shovel', '') == 'on'
    con['signal_mirror'] = request.POST.get('signalmirror', '') == 'on'
    con['space_blanket'] = request.POST.get('spaceblanket', '') == 'on'
    con['spare_battery'] = request.POST.get('sparebattery', '') == 'on'
    con['tent'] = request.POST.get('tent', '') == 'on'
    con['whistle'] = request.POST.get('whistle', '') == 'on'

    con['days_of_food'] = request.POST.get('daysoffood')
    con['weapon'] = request.POST.get('weapon')
    con['radio_monitor_time'] = request.POST.get('radiomonitortime')
    con['off_trail_travel'] = request.POST.get('offtrailtravel') == 'yes'
    con['uploaded_files'] = request.FILES.getlist('fileupload')
    con['cell_number'] = request.POST.get('cellnumber')
    con['satellite_number'] = request.POST.get('satellitenumber')

    con['gar_average'] = request.POST.get('garaverage', '')
    con['gar_mitigated'] = request.POST.get('garmitigated', '')
    con['gar_mitigations'] = request.POST.get('garmitigations')
    con['notes'] = request.POST.get('notes')

    return con


def _save_data(context: dict):
    travel = Travel()
    travel.start_date = datetime.strptime(context.get('start_date'), '%Y-%m-%d').date()
    travel.entry_point = Location.objects.filter(name=context.get('entry_point')).first()
    travel.end_date = datetime.strptime(context.get('end_date'), '%Y-%m-%d').date()
    travel.exit_point = Location.objects.filter(name=context.get('exit_point')).first()
    travel.tracked = context.get('tracked')
    travel.plb = context.get('plb')

    user = user_services.add_if_not_present(username=context.get('travelers')[0]['traveler_name'])
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

    travel.days_of_food = context.get('days_of_food')
    travel.weapon = context.get('weapon')
    travel.radio_monitor_time = context.get('radio_monitor_time')
    travel.off_trail_travel = context.get('off_trail_travel')
    travel.cell_number = context.get('cell_number')
    travel.satellite_number = context.get('satellite_number')

    travel.gar_average = _optional_int(context.get('gar_average'))
    travel.gar_mitigated = _optional_int(context.get('gar_mitigated'))
    travel.gar_mitigations = context.get('gar_mitigations')
    travel.notes = context.get('notes')

    travel.save()

    for t in context['travelers']:
        if not t.get('traveler_name'):
            break
        user = user_services.add_if_not_present(username=t.get('traveler_name'))
        user_services.save_profile(user, call_sign=t.get('call_sign'))

        travel_user_unit = TravelUserUnit()
        travel_user_unit.traveler = user
        travel_user_unit.travel = travel

        color = color_services.add_if_not_present(t.get('pack_color'))
        travel_user_unit.pack_color = Color.objects.filter(name=color).first()
        color = color_services.add_if_not_present(t.get('tent_color'))
        travel_user_unit.tent_color = Color.objects.filter(name=color).first()
        color = color_services.add_if_not_present(t.get('fly_color'))
        travel_user_unit.fly_color = Color.objects.filter(name=color).first()

        travel_user_unit.supervision = _optional_int(t.get('supervision'))
        travel_user_unit.planning = _optional_int(t.get('planning'))
        travel_user_unit.contingency = _optional_int(t.get('contingency'))
        travel_user_unit.comms = _optional_int(t.get('comms'))
        travel_user_unit.team_selection = _optional_int(t.get('team_selection'))
        travel_user_unit.fitness = _optional_int(t.get('fitness'))
        travel_user_unit.env = _optional_int(t.get('env'))
        travel_user_unit.complexity = _optional_int(t.get('complexity'))

        travel_user_unit.save()

    for d in context['day_plans']:
        if not d.get('date'):
            break
        day_plan = TravelDayPlan()
        day_plan.travel = travel
        day_plan.date = datetime.strptime(d.get('date'), '%Y-%m-%d')
        day_plan.starting_point = Location.objects.filter(name=d.get('starting_point')).first()
        day_plan.ending_point = Location.objects.filter(name=d.get('ending_point')).first()
        day_plan.route = d.get('route')
        day_plan.mode = d.get('mode')

        day_plan.save()

    for rp in context['contacts']:
        if not rp.get('contact_name'):
            break
        contact = user_services.add_if_not_present(rp.get('contact_name'), rp.get('contact_email'))
        user_services.save_profile(contact, 
                                   work_number=rp.get('contact_work'),
                                   home_number=rp.get('contact_home'),
                                   cell_number=rp.get('contact_cell'),)
        travel.contacts.add(contact)

    travel.save()

    travel = Travel.objects.get(id=travel.id)
    base_name = file_utils.generate_name(travel.trip_leader.username, travel.start_date.strftime('%Y%m%d'))
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
