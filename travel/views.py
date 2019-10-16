from django.shortcuts import render
from .models import Travel


def entry(request):
    context = {

    }
    return render(request, 'travel/entry.html', context)


def search(request):
    context = {
        'title': 'Search',
        'travels': Travel.objects.all()
    }
    return render(request, 'travel/search.html', context)
