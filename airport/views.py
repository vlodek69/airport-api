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
    FlightDetailSerializer,
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
    queryset = Airplane.objects.all()
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
    queryset = Airport.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        return AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

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
    queryset = Flight.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
