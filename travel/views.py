from datetime import datetime
from copy import deepcopy

from django.http import HttpRequest
from django.shortcuts import render
from .models import Location, Travel

context = {
    'title': 'Travel Plan Entry',
    'locations': Location.objects.values_list('name', flat=True),
    'error': '',
    'start_date': '',
    'entry_point': '',
    'end_date': '',
    'exit_point': '',
    'tracked': True,
}

for i in range(4):
    context['travelername' + str(i)] = ''
    context['callsign' + str(i)] = ''
    context['packcolor' + str(i)] = ''
    context['tentcolor' + str(i)] = ''
    context['flycolor' + str(i)] = ''


def entry(request: HttpRequest):
    con = deepcopy(context)

    if request.method == 'POST':
        con = _fill_context(request)
        con = _create_travelers(request, con)

        _validate(request, con)
        if con.get('error'):
            return render(request, 'travel/entry.html', con)

        _save_data(con)

        return render(request, 'travel/entry.html', con)
    else:
        con = _create_travelers(request, con)
    return render(request, 'travel/entry.html', con)


def search(request: HttpRequest):
    return render(request, 'travel/search.html', context)


def _create_travelers(request: HttpRequest, context: dict) -> dict:
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
    # datetime.strptime(context.get('end_date'), '%Y-%m-%d').date()
    a = context.get('end_date')
    b = context.get('start_date')
    c = datetime.strptime(context.get('end_date'), '%Y-%m-%d')
    d = datetime.strptime(context.get('start_date'), '%Y-%m-%d')
    e = datetime.strptime(context.get('end_date'), '%Y-%m-%d') < datetime.strptime(context.get('start_date'), '%Y-%m-%d')

    if not (context.get('end_date') and context.get('start_date')
            and datetime.strptime(context.get('end_date'), '%Y-%m-%d') >
            datetime.strptime(context.get('start_date'), '%Y-%m-%d')):
        context['error'] = "Your exit date can't be before your entry date."

    # if self.start_date != self.day_plans[0]['date']:
    #     self.error = "Your days' plans should start on your entry date. " \
    #                  "The two dates don't match. You have days that are unaccounted for."
    #
    # for plan in reversed(self.day_plans):
    #     if plan['date'] != '':
    #         if self.end_date != plan['date']:
    #             self.error = "Your days' plans should end on your exit date. " \
    #                          "The two dates don't match. You have days that are unaccounted for."
    #         break

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
    con['start_date'] = request.POST['startdate']
    con['entry_point'] = request.POST['entrypoint']
    con['end_date'] = request.POST['enddate']
    con['exit_point'] = request.POST['exitpoint']
    con['tracked'] = request.POST['tracked'] == 'yes'
    con['plb'] = request.POST['plb']

    con = _create_travelers(request, con)

    return con


def _save_data(context: dict):
    travel = Travel()
    travel.start_date = datetime.strptime(context.get('start_date'), '%Y-%m-%d').date()
    travel.entry_point = Location.objects.filter(name=context.get('entry_point')).first()
    travel.end_date = datetime.strptime(context.get('end_date'), '%Y-%m-%d').date()
    travel.exit_point = Location.objects.filter(name=context.get('exit_point')).first()
    travel.tracked = context.get('tracked')
    travel.plb = context.get('plb')

    travel.save()
