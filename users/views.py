from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from travel.models import TravelUserUnit, Travel
from users.models import Profile


def get_user_profile_by_username(request: HttpRequest):
    if request.method == 'GET':
        username = request.GET.get('username', '').strip()
        traveler_unit: TravelUserUnit = TravelUserUnit.objects.filter(traveler__username=username)\
            .order_by('-travel__start_date').order_by('-travel__created_date').first()
    else:
        traveler_unit: TravelUserUnit = TravelUserUnit()

    response = {'username': traveler_unit.traveler.username,
                'call_sign': traveler_unit.traveler.profile.call_sign,
                'pack_color': '' if not traveler_unit.pack_color else traveler_unit.pack_color.name,
                'tent_color': '' if not traveler_unit.tent_color else traveler_unit.tent_color.name,
                'fly_color': '' if not traveler_unit.fly_color else traveler_unit.fly_color.name,
                'email': traveler_unit.traveler.email,
                'work_phone': traveler_unit.traveler.profile.work_number,
                'home_phone': traveler_unit.traveler.profile.home_number,
                'cell_phone': traveler_unit.traveler.profile.cell_number,
                }

    return JsonResponse(response)

