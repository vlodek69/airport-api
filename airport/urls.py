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
    TicketViewSet,
)

router = routers.DefaultRouter()
router.register("genres", AirplaneTypeViewSet)
router.register("actors", SeatClassViewSet)
router.register("cinema_halls", AirplaneViewSet)
router.register("movies", CountryViewSet)
router.register("movie_sessions", AirportViewSet)
router.register("orders", RouteViewSet)
router.register("orders", CrewViewSet)
router.register("orders", FlightViewSet)
router.register("orders", OrderViewSet)
router.register("orders", TicketViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
