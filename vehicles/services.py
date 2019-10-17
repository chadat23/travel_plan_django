from .models import Vehicle
from colors import services as color_services
from colors.models import Color
from departments.models import Department


def add_if_not_present(plate: str, make: str = None, model: str = None, color: str = None,
                       location: str = None, active: bool = None, department: str = None) -> str:

    vehicle = Vehicle.objects.filter(plate=plate).first()
    if not vehicle:
        vehicle = Vehicle()
        vehicle.plate = plate
        if make:
            vehicle.make = make
        if model:
            vehicle.model = model
        if color:
            color = color_services.add_if_not_present(color)
            vehicle.color = Color.objects.filter(name=color).first()
        if location:
            vehicle.location = location
        if active != None:
            vehicle.active = active
        if department:
            vehicle.department = Department.objects.filter(name=department).first()

        vehicle.save()

    return vehicle
