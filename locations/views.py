from django.shortcuts import render
from .models import Location


def propose(request):
    return render(request, 'locations/propose.html')
