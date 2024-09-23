from django.shortcuts import render, get_object_or_404
from .models import Restaurant
from .google_places_api import get_place_details

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Fetch Google Place details
    place_details = get_place_details(restaurant.google_place_id)
    
    context = {
        'restaurant': restaurant,
        'google_rating': place_details.get('rating', 'N/A'),
        'google_reviews': place_details.get('reviews', [])
    }
    return render(request, 'restaurants/restaurant_detail.html', context)