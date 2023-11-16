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
)

admin.site.register(AirplaneType)
admin.site.register(Ticket)
admin.site.register(Order)
admin.site.register(Flight)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Airport)
admin.site.register(Country)
admin.site.register(Airplane)
admin.site.register(SeatClass)
