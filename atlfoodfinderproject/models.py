from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_information = models.CharField(max_length=100)
    cuisine_type = models.CharField(max_length=100)
    rating = models.FloatField(default=0.0)
    google_place_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name