from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    SeatClassViewSet,
    AirplaneViewSet,
    CountryViewSet,
    AirportViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    CabinViewSet,
)

viewset_dict = {
    "airplane-types": AirplaneTypeViewSet,
    "seat-classes": SeatClassViewSet,
    "cabins": CabinViewSet,
    "airplanes": AirplaneViewSet,
    "countries": CountryViewSet,
    "airports": AirportViewSet,
    "routes": RouteViewSet,
    "crew": CrewViewSet,
    "flights": FlightViewSet,
    "orders": OrderViewSet,
}

router = routers.DefaultRouter()

for viewset_prefix, viewset_class in viewset_dict.items():
    router.register(viewset_prefix, viewset_class)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
