from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from vehicles.models import Vehicle


def get_vehicle_by_plate(request: HttpRequest):
    if request.method == 'GET':
        plate = request.GET.get('plate', '').split(' ')[0]
        vehicle = Vehicle.objects.get(plate=plate)
    else:
        vehicle = Vehicle()

    color = '' if not vehicle.color else vehicle.color.name
    response = {'plate': vehicle.plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'color': color,
                'location': vehicle.location,
                }

    return JsonResponse(response)

