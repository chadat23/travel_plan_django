from copy import deepcopy
from datetime import datetime
import os
from typing import Optional, List

from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect

from .models import Travel, TravelUserUnit, TravelDayPlan
from colors.models import Color
from colors import services as color_services
from locations.models import Location
from travel_utils import file_utils, pdf_util, email_util
from users import services as user_services
from vehicles.models import Vehicle
from vehicles import services as vehicle_services


def entry(request: HttpRequest):
    context = {
        'title': 'Travel Plan Entry',
        'colors': Color.objects.order_by('name').values_list('name', flat=True),
        'locations': Location.objects.order_by('name').values_list('name', flat=True),
        'usernames': User.objects.order_by('-username').filter(profile__active=True).values_list('username', flat=True),
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

        email_util.email_travel(travel, files, path)

        return render(request, 'travel/entry.html', context)
        # return redirect('travel-sent')
    else:
        context = _fill_travelers(request, context)
        context = _fill_day_plans(request, context)
        context = _fill_contacts(request, context)
    return render(request, 'travel/entry.html', context)


def search(request: HttpRequest):
    context = {}
    return render(request, 'travel/search.html', context)


def sent(request: HttpRequest):
    return render(request, 'travel/sent.html', {})


def get_traveluserunit_call_sign_and_gear(request: HttpRequest):
    if request.method == 'GET':
        username = request.GET.get('username', '').strip()
        traveluserunit: dict = TravelUserUnit.objects.filter(traveler__username=username)\
            .order_by('-travel__start_date', '-created_date')\
            .values('traveler__profile__call_sign', 'pack_color__name', 'tent_color__name', 'fly_color__name').first()

        traveluserunit['call_sign'] = traveluserunit['traveler__profile__call_sign']
        traveluserunit['pack_color'] = traveluserunit['pack_color__name']
        traveluserunit['tent_color'] = traveluserunit['tent_color__name']
        traveluserunit['fly_color'] = traveluserunit['fly_color__name']
    else:
        traveluserunit = {}

    return JsonResponse(traveluserunit)


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
            t['total'] = request.POST.get('total' + str(1), '')
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


def _fill_context(request: HttpRequest, context) -> dict:

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

    return context


def _save_data(context: dict):
    travel = Travel()
    travel.start_date = datetime.strptime(context.get('start_date'), '%Y-%m-%d').date()
    travel.entry_point = Location.objects.filter(name=context.get('entry_point')).first()
    travel.end_date = datetime.strptime(context.get('end_date'), '%Y-%m-%d').date()
    travel.exit_point = Location.objects.filter(name=context.get('exit_point')).first()
    travel.tracked = context.get('tracked')
    travel.plb = context.get('plb')

    user = user_services.add_if_not_present(username=context.get('travelers')[0]['traveler_name'])
    # user =
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

    travel.save()

    for t in context['travelers']:
        if not t.get('traveler_name'):
            break
        # user = user_services.add_if_not_present(username=t.get('traveler_name'))
        user, created = User.objects.get_or_create(username=t.get('traveler_name').strip())
        user_services.save_profile(user, t.get('call_sign'), None, None, None, None, None)

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

    for d in context['day_plans']:
        if not d.get('date'):
            break
        day_plan = TravelDayPlan()
        day_plan.travel = travel
        day_plan.date = datetime.strptime(d.get('date'), '%Y-%m-%d')
        day_plan.starting_point = Location.objects.filter(name=d.get('starting_point')).first()
        day_plan.ending_point = Location.objects.filter(name=d.get('ending_point')).first()
        day_plan.route = d.get('route') if d.get('route') else None
        day_plan.mode = d.get('mode') if d.get('mode') else None

        day_plan.save()

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


def _optional_float(numb: str) -> Optional[int]:
    if not numb:
        return
    try:
        return float(numb)
    except:
        return
