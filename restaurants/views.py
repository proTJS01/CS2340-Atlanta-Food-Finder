# restaurants/views.py
import logging
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Restaurant, Favorite, Review
from .forms import RegisterForm, ReviewForm

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

        # Logging received data
        logger.debug(f"Received add_favorite POST data: place_id={place_id}, name={name}, address={address}, rating={rating}")

        if not place_id:
            logger.warning(f"Attempted to add favorite without place_id: name={name}, address={address}")
            return JsonResponse({'message': 'Place ID is required.'}, status=400)

        # Fetch restaurant details from Google Places API
        try:
            url = (
                f"https://maps.googleapis.com/maps/api/place/details/json?"
                f"place_id={place_id}&"
                f"fields=name,formatted_address,geometry,types,formatted_phone_number&"
                f"key={API_KEY}"
            )
            response = requests.get(url)
            data = response.json()

            if data.get('status') == 'OK':
                result = data.get('result', {})
                geometry = result.get('geometry', {})
                location = geometry.get('location', {})
                latitude = location.get('lat', 0.0)
                longitude = location.get('lng', 0.0)
                types = result.get('types', [])
                formatted_phone_number = result.get('formatted_phone_number', 'No phone number provided')

                # Extract cuisine type from types
                cuisine_type = "Unknown"
                cuisine_keywords = ['restaurant', 'cafe', 'bar', 'bistro', 'diner', 'eatery', 'pub']
                for t in types:
                    if t not in cuisine_keywords:
                        cuisine_type = t.replace('_', ' ').title()
                        break
            else:
                logger.error(
                    f"Google Places API error for place_id={place_id}: "
                    f"status={data.get('status')}, error_message={data.get('error_message', '')}"
                )
                latitude = 0.0
                longitude = 0.0
                cuisine_type = "Unknown"
                formatted_phone_number = 'No phone number provided'
        except Exception as e:
            logger.exception(f"Exception while fetching place details for place_id={place_id}: {e}")
            latitude = 0.0
            longitude = 0.0
            cuisine_type = "Unknown"
            formatted_phone_number = 'No phone number provided'

        # Ensure the Restaurant object exists with correct latitude and longitude
        restaurant, created = Restaurant.objects.get_or_create(
            place_id=place_id,
            defaults={
                'name': name,
                'address': address,
                'latitude': latitude,
                'longitude': longitude,
                'cuisine_type': cuisine_type,
                'formatted_phone_number': formatted_phone_number
            }
        )

        if not created:
            # Optionally, update existing Restaurant data if necessary
            updated = False
            if restaurant.name == 'Unknown' and name != 'Unknown':
                restaurant.name = name
                updated = True
            if restaurant.address == 'No address available' and address != 'No address available':
                restaurant.address = address
                updated = True
            if restaurant.cuisine_type == 'Unknown' and cuisine_type != 'Unknown':
                restaurant.cuisine_type = cuisine_type
                updated = True
            if restaurant.formatted_phone_number == 'No phone number provided' and formatted_phone_number != 'No phone number provided':
                restaurant.formatted_phone_number = formatted_phone_number
                updated = True
            if updated:
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
        url = (
            f"https://maps.googleapis.com/maps/api/place/details/json?"
            f"place_id={place_id}&"
            f"fields=name,formatted_address,geometry,rating,types,formatted_phone_number,opening_hours&"
            f"key={API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        if data.get('status') == 'OK':
            details = data.get('result', {})
            geometry = details.get('geometry', {})
            location = geometry.get('location', {})
            latitude = location.get('lat', 0.0)
            longitude = location.get('lng', 0.0)
            name = details.get('name', 'Unknown')
            address = details.get('formatted_address', 'No address available')
            formatted_phone_number = details.get('formatted_phone_number', 'No phone number provided')
            types = details.get('types', [])
            # Extract cuisine type from types
            cuisine_type = "Unknown"
            cuisine_keywords = ['restaurant', 'cafe', 'bar', 'bistro', 'diner', 'eatery', 'pub']
            for t in types:
                if t not in cuisine_keywords:
                    cuisine_type = t.replace('_', ' ').title()
                    break
            # Create the Restaurant object
            restaurant = Restaurant.objects.create(
                place_id=place_id,
                name=name,
                address=address,
                latitude=latitude,
                longitude=longitude,
                cuisine_type=cuisine_type,
                formatted_phone_number=formatted_phone_number
            )
            logger.info(f"Created new Restaurant object: {restaurant}")
        else:
            logger.error(
                f"Google Places API error for restaurant_detail: place_id={place_id}, "
                f"status={data.get('status')}, error_message={data.get('error_message', '')}"
            )
            return render(request, 'restaurants/restaurant_detail.html', {
                'error': 'Details not found.',
                'error_detail': data.get('error_message', '')
            })

    # At this point, we have the restaurant object
    try:
        # Fetch additional details using Google Places API to ensure latest information
        url = (
            f"https://maps.googleapis.com/maps/api/place/details/json?"
            f"place_id={place_id}&"
            f"fields=name,formatted_address,geometry,rating,types,formatted_phone_number,opening_hours&"
            f"key={API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        if data.get('status') == 'OK':
            details = data.get('result', {})
            # Update Restaurant object with latest details
            types = details.get('types', [])
            cuisine_type = restaurant.cuisine_type
            cuisine_keywords = ['restaurant', 'cafe', 'bar', 'bistro', 'diner', 'eatery', 'pub']
            for t in types:
                if t not in cuisine_keywords:
                    new_cuisine_type = t.replace('_', ' ').title()
                    if new_cuisine_type != cuisine_type:
                        restaurant.cuisine_type = new_cuisine_type
                        restaurant.save()
                    break
            # Update phone number if changed
            new_phone_number = details.get('formatted_phone_number', restaurant.formatted_phone_number)
            if new_phone_number != restaurant.formatted_phone_number:
                restaurant.formatted_phone_number = new_phone_number
                restaurant.save()

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
                'user_reviews': user_reviews,
                'latitude': restaurant.latitude,  # Pass latitude
                'longitude': restaurant.longitude,  # Pass longitude
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,  # Pass API Key
            }
            return render(request, 'restaurants/restaurant_detail.html', context)
        else:
            logger.error(
                f"Google Places API error in restaurant_detail: place_id={place_id}, "
                f"status={data.get('status')}, error_message={data.get('error_message', '')}"
            )
            return render(request, 'restaurants/restaurant_detail.html', {
                'error': 'Details not found.',
                'error_detail': data.get('error_message', '')
            })
    except Exception as e:
        logger.exception(f"Exception in restaurant_detail view for place_id={place_id}: {e}")
        return render(request, 'restaurants/restaurant_detail.html',
                      {'error': 'An error occurred while fetching details.', 'error_detail': str(e)})
