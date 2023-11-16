from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


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


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    seats_economy = models.IntegerField(default=0)
    seats_business = models.IntegerField(default=0)
    seats_first_class = models.IntegerField(default=0)
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return sum(
            (self.seats_economy, self.seats_business, self.seats_first_class)
        )


class Country(models.Model):
    name = models.CharField(max_length=63)

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
        return f"{self.departure}-{self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    class Meta:
        verbose_name_plural = "Crew"

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{str(self.route)} {self.departure_time}"

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE)
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(seat_class, seat, airplane, error_to_raise):
        max_seat = getattr(airplane, "seats_" + seat_class.name.lower())
        if not 1 <= seat <= max_seat:
            raise error_to_raise

    def clean(self):
        Ticket.validate_ticket(
            self.seat_class,
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
            f"(seat: {self.seat}, seat_class: {str(self.seat_class)}"
        )

    class Meta:
        unique_together = ("flight", "seat_class", "seat")
        ordering = ["seat_class", "seat"]
