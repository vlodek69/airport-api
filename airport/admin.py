from django.contrib import admin

from airport.models import (
    SeatClass,
    Airplane,
    Country,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
    AirplaneType,
    Cabin,
)


model_list = [
    SeatClass,
    Airplane,
    Country,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
    AirplaneType,
    Cabin,
]

for model in model_list:
    admin.site.register(model)
