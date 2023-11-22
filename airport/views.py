from datetime import datetime

from django.db.models import Count, F, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
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
)
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
    OrderListSerializer,
    FlightListSerializer,
    AirplaneListSerializer,
    RouteListSerializer,
    AirportListSerializer,
    FlightDetailSerializer,
    RouteDetailSerializer,
    CountryImageSerializer,
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class SeatClassViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = SeatClass.objects.all()
    serializer_class = SeatClassSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.select_related("airplane_type")

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

    def get_serializer_class(self):
        if self.action == "upload_image":
            return CountryImageSerializer

        return CountrySerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific country"""
        country = self.get_object()
        serializer = self.get_serializer(country, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.select_related("country")

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
    queryset = Route.objects.select_related(
        "departure__country", "destination__country"
    )

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


class BasePagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.prefetch_related("crew")
        .select_related(
            "route__departure__country",
            "route__destination__country",
            "airplane",
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
    pagination_class = BasePagination

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
            departure_date = datetime.strptime(
                departure_date, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(departure_time__date=departure_date)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "from",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by departure city, country or airport name "
                    "(ex. ?from=Kyiv)"
                ),
            ),
            OpenApiParameter(
                "to",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by destination city, country or airport name "
                    "(ex. ?to=Krakow)"
                ),
            ),
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by date of DEPARTURE " "(ex. ?date=2024-04-19)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    pagination_class = BasePagination
    permission_classes = (IsAuthenticated,)

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
