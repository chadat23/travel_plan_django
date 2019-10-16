from django.shortcuts import render


def entry(request):
    context = {

    }
    return render(request, 'travel/entry.html', context)


def search(request):
    return render(request, 'travel/search.html', {'title': 'maybe?'})
