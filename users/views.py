from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from travel.models import TravelUserUnit, Travel
from users.models import Profile


def get_user_contact_info(request: HttpRequest):
    if request.method == 'GET':
        name = request.GET.get('name', '').strip()
        user: dict = Profile.objects.filter(name=name)\
            .values('user__email', 'work_number', 'home_number', 'cell_number').first()

        if user:
            user['email'] = user.pop('user__email')
        else:
            user = {}
    else:
        user = {}

    return JsonResponse(user)
