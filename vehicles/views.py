from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from vehicles.models import Vehicle


def get_vehicle_by_plate(request: HttpRequest):
    if request.method == 'GET':
        plate = request.GET.get('plate', '').split(' ')[0]
        vehicle = Vehicle.objects.filter(plate=plate).values('plate', 'make', 'model', 'color__name').first()
        vehicle['color'] = vehicle['color__name']
    else:
        vehicle = {}

    return JsonResponse(vehicle)

