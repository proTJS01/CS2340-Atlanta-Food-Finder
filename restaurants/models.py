from django.db import models
from django_google_maps import fields as map_fields

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = map_fields.AddressField(max_length=255)  # This will store the address
    latitude = models.FloatField()  # Latitude as a float
    longitude = models.FloatField()  # Longitude as a float
    cuisine_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name