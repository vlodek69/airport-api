from datetime import datetime

from django.db.models import Count, F, Q
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from airport.models import (
    AirplaneType,
    SeatClass,
    Airplane,
    Country,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirplaneTypeSerializer,
    SeatClassSerializer,
    AirplaneSerializer,
    CountrySerializer,
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
    OrderListSerializer,
    FlightListSerializer,
    AirplaneListSerializer,
    RouteListSerializer,
    AirportListSerializer,
    FlightDetailSerializer, RouteDetailSerializer,
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class SeatClassViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.select_related("airplane_type")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        return AirplaneSerializer


class CountryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.select_related("country")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        return AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.select_related("departure__country", "destination__country")
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .prefetch_related("crew")
        .select_related(
            "route__departure__country",
            "route__destination__country",
            "airplane"
        )
        .annotate(
            tickets_available=(
                F("airplane__seats_economy")
                + F("airplane__seats_business")
                + F("airplane__seats_first_class")
                - Count("tickets")
            )
        )
    )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        departure = self.request.query_params.get("from")
        destination = self.request.query_params.get("to")
        departure_date = self.request.query_params.get("date")

        queryset = self.queryset

        if departure:
            queryset = queryset.filter(
                Q(route__departure__name__icontains=departure)
                | Q(route__departure__near_city__icontains=departure)
                | Q(route__departure__country__name__icontains=departure)
            )

        if destination:
            queryset = queryset.filter(
                Q(route__destination__name__icontains=destination)
                | Q(route__destination__near_city__icontains=destination)
                | Q(route__destination__country__name__icontains=destination)
            )

        if departure_date:
            departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=departure_date)

        return queryset


    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the orders with currently authenticated user"""
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        """Create the orders with currently authenticated user"""
        serializer.save(user=self.request.user)
