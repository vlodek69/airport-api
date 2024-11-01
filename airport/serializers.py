from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    AirplaneType,
    SeatClass,
    Airplane,
    Country,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order,
    Cabin,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class SeatClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatClass
        fields = ("id", "name")


class CabinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabin
        fields = ("id", "name", "seat_class", "seats")


class CabinListSerializer(CabinSerializer):
    seat_class = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )


class CabinListSerializerLight(CabinListSerializer):
    class Meta:
        model = Cabin
        fields = ("id", "seat_class", "seats")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "cabins",
            "airplane_type",
        )


class AirplaneListSerializer(AirplaneSerializer):
    cabins = CabinListSerializerLight(many=True, read_only=True)
    airplane_capacity = serializers.IntegerField(
        source="capacity", read_only=True
    )
    airplane_type = serializers.StringRelatedField()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "cabins",
            "airplane_capacity",
            "airplane_type",
        )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CountryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "image")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "near_city", "country")


class AirportListSerializer(AirportSerializer):
    country = serializers.CharField(source="country.name", read_only=True)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "departure", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    departure = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()
    distance = serializers.CharField(source="distance_km", read_only=True)


class RouteDetailSerializer(RouteSerializer):
    departure = AirportListSerializer()
    destination = AirportListSerializer()
    distance = serializers.CharField(source="distance_km", read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crew",
            "airplane",
            "departure_time",
            "arrival_time",
        )


class FlightListSerializer(FlightSerializer):
    airplane = serializers.StringRelatedField(many=False)
    route = serializers.StringRelatedField(many=False)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )


class FlightDetailSerializer(FlightSerializer):
    airplane = AirplaneListSerializer()
    route = RouteDetailSerializer()
    crew = serializers.StringRelatedField(many=True)
    tickets_available = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(
        source="route.destination.country.image", read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crew",
            "airplane",
            "tickets_available",
            "departure_time",
            "arrival_time",
            "image",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cabin"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cabin", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    cabin = serializers.CharField(
        source="cabin.seat_class.name", read_only=True
    )
    flight = FlightListSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
