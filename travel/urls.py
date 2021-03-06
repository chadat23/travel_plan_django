"""travel_plan_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry),
    path('ajax-get-userunit-call-sign-and-gear/', views.get_traveluserunit_call_sign_and_gear,
         name='ajax-traveluserunit-call-sign-and-gear'),
    path('entry/', views.entry, name='travel-entry'),
    path('date-range-itineraries-map/', views.date_range_itineraries_map, 
         name='travel-date-range-itineraries-map'),
    path('search/', views.search, name='travel-search'),
    path('sent/', views.sent, name='travel-sent'),
    path('saved/', views.saved, name='travel-saved'),
    path('itinerary-map/', views.itinerary_map, name='travel-itinerary-map')
]
