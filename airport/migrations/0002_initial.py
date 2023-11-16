# Generated by Django 4.2.7 on 2023-11-16 15:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("airport", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="flight",
            name="airplane",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="airport.airplane"
            ),
        ),
        migrations.AddField(
            model_name="flight",
            name="crew",
            field=models.ManyToManyField(related_name="flights", to="airport.crew"),
        ),
        migrations.AddField(
            model_name="flight",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="airport.route"
            ),
        ),
        migrations.AddField(
            model_name="airport",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="airport.country"
            ),
        ),
        migrations.AddField(
            model_name="airplane",
            name="airplane_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="airport.airplanetype"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("flight", "seat_class", "seat")},
        ),
    ]