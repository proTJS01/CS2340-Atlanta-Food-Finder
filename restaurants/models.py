# restaurants/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    cuisine_type = models.CharField(max_length=100, default="Unknown")
    place_id = models.CharField(max_length=255, unique=True)  # Enforce uniqueness
    formatted_phone_number = models.CharField(max_length=20, blank=True, null=True)  # Renamed field

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('restaurant_detail', args=[self.place_id])

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    place_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255, default='Unknown')  # Assign default
    address = models.CharField(max_length=255, blank=True, null=True, default='No address available')
    rating = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'place_id')  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # Rating out of 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Newest reviews first

    def __str__(self):
        return f"Review by {self.user.username} for {self.restaurant.name}"