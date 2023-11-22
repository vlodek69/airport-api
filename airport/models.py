import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class AirplaneType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class SeatClass(models.Model):
    name = models.CharField(max_length=63)

    class Meta:
        verbose_name_plural = "Seat Classes"

    def __str__(self):
        return self.name


class Cabin(models.Model):
    name = models.CharField(max_length=63)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE)
    seats = models.IntegerField()

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    cabins = models.ManyToManyField(Cabin, related_name="airplanes")
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return sum(cabin.seats for cabin in self.cabins.all())


def country_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/countries/", filename)


class Country(models.Model):
    name = models.CharField(max_length=63)
    image = models.ImageField(null=True, upload_to=country_image_file_path)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=63)
    near_city = models.CharField(max_length=63)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Route(models.Model):
    departure = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routs"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routs"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{str(self.departure)}-{str(self.destination)}"

    @property
    def name(self):
        return f"{self.departure.name}-{self.destination.name}"

    @property
    def distance_km(self):
        return f"{self.distance} km"


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        verbose_name_plural = "Crew"

    def __str__(self):
        return self.first_name + " " + self.last_name


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return (
            f"{str(self.route)} "
            f"{self.departure_time.strftime('%Y-%m-%d %H:%M')}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M')


class Ticket(models.Model):
    cabin = models.ForeignKey(Cabin, on_delete=models.CASCADE)
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("flight", "cabin", "seat")
        ordering = ["cabin", "seat"]

    @staticmethod
    def validate_ticket(cabin, seat, airplane, error_to_raise):
        cabins = getattr(airplane, "cabins")
        if cabin not in cabins.all():
            raise error_to_raise(f"Airplane has no cabin '{cabin.name}'")
        if not 1 <= seat <= cabin.seats:
            raise error_to_raise(
                f"Seat number must be in range (1, {cabin.seats})"
            )

    def clean(self):
        Ticket.validate_ticket(
            self.cabin,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{str(self.flight)} "
            f"(seat: {self.seat}, seat_class: {self.cabin.seat_class.name}"
        )
