from datetime import datetime
from copy import deepcopy

from django.http import HttpRequest
from django.shortcuts import render
from .models import Location, Travel

context = {
    'title': 'Travel Plan Entry',
    'locations': Location.objects.values_list('name', flat=True),
    'start_date': '',
    'entry_point': '',
    'end_date': '',
    'exit_point': '',
    'tracked': True,
}


def entry(request: HttpRequest):
    if request.method == 'POST':
        con = _fill_context(request)

        _save_data(con)
    else:
        con = context
    return render(request, 'travel/entry.html', con)


def search(request: HttpRequest):
    return render(request, 'travel/search.html', context)


def _fill_context(request: HttpRequest) -> dict:
    con = deepcopy(context)
    con['start_date'] = request.POST['startdate']
    con['entry_point'] = request.POST['entrypoint']
    con['end_date'] = request.POST['enddate']
    con['exit_point'] = request.POST['exitpoint']
    con['tracked'] = request.POST['tracked'] == 'yes'
    con['plb'] = request.POST['plb']
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
