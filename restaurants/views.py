# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Restaurant, Favorite, Review
from .forms import RegisterForm, ReviewForm
import requests
import logging

logger = logging.getLogger(__name__)

API_KEY = settings.GOOGLE_MAPS_API_KEY  # Use API key from Django settings


# Registration View
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('profile')  # Redirect to profile or home page
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# Profile View with Favorites
@login_required
def profile(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'registration/profile.html', {'favorites': favorites})


# Add Favorite View
@login_required
def add_favorite(request):
    if request.method == 'POST':
        place_id = request.POST.get('place_id')
        name = request.POST.get('name') or 'Unknown'  # Assign default if name is missing
        address = request.POST.get('address') or 'No address available'  # Assign default if address is missing
        rating = request.POST.get('rating')  # Rating can remain as is; it's optional

        if not place_id:
            logger.warning(f"Attempted to add favorite without place_id: name={name}, address={address}")
            return JsonResponse({'message': 'Place ID is required.'}, status=400)

        # Fetch restaurant details from Google Places API
        try:
            url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=geometry&key={API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data.get('status') == 'OK':
                geometry = data.get('result', {}).get('geometry', {})
                location = geometry.get('location', {})
                latitude = location.get('lat', 0.0)
                longitude = location.get('lng', 0.0)
            else:
                logger.error(f"Google Places API error for place_id={place_id}: {data.get('status')}")
                latitude = 0.0
                longitude = 0.0
        except Exception as e:
            logger.exception(f"Exception while fetching place details for place_id={place_id}: {e}")
            latitude = 0.0
            longitude = 0.0

        # Ensure the Restaurant object exists with correct latitude and longitude
        restaurant, created = Restaurant.objects.get_or_create(
            place_id=place_id,
            defaults={
                'name': name,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'cuisine_type': 'Unknown'
            }
        )

        if not created:
            # Optionally, update existing Restaurant data if necessary
            if restaurant.name == 'Unknown' and name != 'Unknown':
                restaurant.name = name
                restaurant.save()
            if restaurant.address == 'No address available' and address != 'No address available':
                restaurant.address = address
                restaurant.save()

        # Check if the favorite already exists for the user
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            place_id=place_id,
            defaults={
                'name': name,
                'address': address,
                'rating': rating if rating else None
            }
        )
        if created:
            message = "Added to favorites."
            logger.info(f"User {request.user.username} added favorite: {favorite}")
        else:
            message = "Already in favorites."
            logger.info(f"User {request.user.username} attempted to add existing favorite: {favorite}")
        return JsonResponse({'message': message})
    else:
        logger.warning(f"Invalid request method for add_favorite: {request.method}")
        return JsonResponse({'message': 'Invalid request.'}, status=400)


# Remove Favorite View
@login_required
def remove_favorite(request, place_id):
    if request.method == 'POST':
        favorite = get_object_or_404(Favorite, user=request.user, place_id=place_id)
        favorite.delete()
        logger.info(f"User {request.user.username} removed favorite: {favorite}")
        return JsonResponse({'message': 'Removed from favorites.'})
    else:
        logger.warning(f"Invalid request method for remove_favorite: {request.method}")
        return JsonResponse({'message': 'Invalid request.'}, status=400)


# Map View for displaying restaurants
def map_view(request):
    # Pass user's favorite place_ids to the template for determining favorite status
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(request.user.favorites.all().values_list('place_id', flat=True))
    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'user_favorites': user_favorites,
    }
    return render(request, 'restaurants/map.html', context)


# Fetch detailed restaurant information via Google Places API
def restaurant_detail(request, place_id):
    # Attempt to retrieve the Restaurant object from the database
    restaurant = Restaurant.objects.filter(place_id=place_id).first()

    if not restaurant:
        # Attempt to fetch restaurant details from Google Places API
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,geometry,rating,reviews,opening_hours&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'OK':
            details = data.get('result')
            geometry = details.get('geometry', {})
            location = geometry.get('location', {})
            latitude = location.get('lat', 0.0)
            longitude = location.get('lng', 0.0)
            name = details.get('name', 'Unknown')
            address = details.get('formatted_address', 'No address available')

            # Create the Restaurant object
            restaurant = Restaurant.objects.create(
                place_id=place_id,
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                cuisine_type='Unknown'  # You might want to fetch this from API as well
            )
            logger.info(f"Created new Restaurant object: {restaurant}")
        else:
            logger.error(
                f"Google Places API error for restaurant_detail: place_id={place_id}, status={data.get('status')}")
            return render(request, 'restaurants/restaurant_detail.html', {'error': 'Details not found.'})

    # Fetch additional details using Google Places API
    try:
        url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,geometry,rating,reviews,opening_hours&key={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'OK':
            details = data.get('result')
            is_favorite = False
            if request.user.is_authenticated:
                is_favorite = Favorite.objects.filter(user=request.user, place_id=place_id).exists()

            # Handle review submission
            if request.method == 'POST':
                form = ReviewForm(request.POST)
                if form.is_valid():
                    review = form.save(commit=False)
                    review.user = request.user
                    review.restaurant = restaurant
                    review.save()
                    logger.info(f"User {request.user.username} submitted a review for {restaurant}")
                    return redirect('restaurant_detail', place_id=place_id)
            else:
                form = ReviewForm()

            # Fetch user reviews from your database
            user_reviews = Review.objects.filter(restaurant=restaurant)

            context = {
                'details': details,
                'is_favorite': is_favorite,
                'form': form,
                'user_reviews': user_reviews
            }
            return render(request, 'restaurants/restaurant_detail.html', context)
        else:
            logger.error(
                f"Google Places API error in restaurant_detail: place_id={place_id}, status={data.get('status')}")
            return render(request, 'restaurants/restaurant_detail.html', {'error': 'Details not found.'})
    except Exception as e:
        logger.exception(f"Exception in restaurant_detail view for place_id={place_id}: {e}")
        return render(request, 'restaurants/restaurant_detail.html',
                      {'error': 'An error occurred while fetching details.'})
