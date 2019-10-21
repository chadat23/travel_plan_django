from django.contrib.auth.models import User
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from travel.models import TravelUserUnit, Travel
from users.models import Profile


def get_user_contact_info(request: HttpRequest):
    if request.method == 'GET':
        username = request.GET.get('username', '').strip()
        user: dict = Profile.objects.filter(user__username=username)\
            .values('user__email', 'work_number', 'home_number', 'cell_number').first()
        user['email'] = user.pop('user__email')
    else:
        user = {}

    return JsonResponse(user)
