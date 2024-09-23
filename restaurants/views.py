from django.shortcuts import render
from .models import Restaurant
import json

def map_view(request):
    # Get all the restaurants from the database
    restaurants = Restaurant.objects.all()
    # Prepare data for Google Maps
    restaurant_data = [
        {
            'name': restaurant.name,
            'latitude': restaurant.latitude,
            'longitude': restaurant.longitude
        }
        for restaurant in restaurants
    ]
    context = {'restaurant_data_json': json.dumps(restaurant_data)}
    return render(request, 'restaurants/map.html', context)
