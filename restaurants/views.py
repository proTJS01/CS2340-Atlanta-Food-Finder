# CS2340App/restaurants/views.py

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

# Define specific cuisine types as per Google Places API
SPECIFIC_CUISINE_TYPES = [
    'italian_restaurant', 'mexican_restaurant', 'chinese_restaurant',
    'japanese_restaurant', 'indian_restaurant', 'thai_restaurant',
    'french_restaurant', 'greek_restaurant', 'spanish_restaurant',
    'american_restaurant', 'korean_restaurant', 'vietnamese_restaurant',
    'mediterranean_restaurant', 'turkish_restaurant', 'lebanese_restaurant',
    'cuban_restaurant', 'peruvian_restaurant',
    # Add more as needed
]

# Known cuisines for fallback inference
KNOWN_CUISINES = [
    'Italian', 'Mexican', 'Chinese', 'Japanese', 'Indian', 'Thai',
    'French', 'Greek', 'Spanish', 'American', 'Korean', 'Vietnamese',
    'Mediterranean', 'Turkish', 'Lebanese', 'Cuban', 'Peruvian',
    'Brazilian', 'Caribbean', 'German', 'British', 'Irish',
    'Portuguese', 'Russian', 'Scandinavian', 'Polish', 'Cajun',
    'Creole', 'Southern', 'Ethiopian', 'Moroccan', 'Argentinian',
    'Canadian', 'Belgian', 'Dutch', 'Swiss', 'Austrian', 'Hungarian',
    'Czech', 'Slovak', 'Ukrainian', 'Filipino', 'Malaysian',
    'Singaporean', 'Indonesian', 'Bangladeshi', 'Pakistani', 'Nepalese',
    # Add more as needed
]


# Home Page View
def home(request):
    """
    Home page view that greets the user with 'Atlanta Food Finder'
    and provides Login and Sign Up buttons.
    """
    return render(request, 'restaurants/home.html')


# Signup View (Renamed from register)
def signup(request):
    """
    User signup view using Django's UserCreationForm.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            logger.info(f"New user registered: {user.username}")
            return redirect('home')
        else:
            logger.warning(f"Signup failed: {form.errors}")
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form': form})

# Add Favorite View
@login_required
def add_favorite(request):
    if request.method == 'POST':
        place_id = request.POST.get('place_id')
        name = request.POST.get('name') or 'Unknown'  # Assign default if name is missing
        address = request.POST.get('address') or 'No address available'  # Assign default if address is missing
        rating = request.POST.get('rating')  # Rating can remain as is; it's optional

        # Logging received data
        logger.debug(
            f"Received add_favorite POST data: place_id={place_id}, name={name}, address={address}, rating={rating}")

        if not place_id:
            logger.warning(f"Attempted to add favorite without place_id: name={name}, address={address}")
            return JsonResponse({'message': 'Place ID is required.'}, status=400)

        # Fetch restaurant details from Google Places API
        try:
            url = (
                f"https://maps.googleapis.com/maps/api/place/details/json?"
                f"place_id={place_id}&"
                f"fields=place_id,name,rating,formatted_address,geometry,types,formatted_phone_number,opening_hours,reviews&"
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
                for t in types:
                    if t in SPECIFIC_CUISINE_TYPES:
                        cuisine_type = t.replace('_restaurant', '').title()
                        break

                # Fallback: Infer from name
                if cuisine_type == "Unknown":
                    for cuisine in KNOWN_CUISINES:
                        if cuisine.lower() in name.lower():
                            cuisine_type = cuisine
                            break

                logger.debug(f"Extracted cuisine_type: {cuisine_type} for place_id: {place_id}")
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
                logger.debug(f"Updated Restaurant object: {restaurant}")

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
        user_favorites = list(Favorite.objects.filter(user=request.user).values_list('place_id', flat=True))
    context = {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'user_favorites': user_favorites,
    }
    return render(request, 'restaurants/map.html', context)


# Favorites Page View
@login_required
def favorites(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user)

    # Enrich favorites with image URLs using Google Places API (optional)
    enriched_favorites = []
    cuisine_set = set()
    for fav in favorites:
        place_id = fav.place_id
        # Fetch details from Google Places API
        params = {
            'place_id': place_id,
            'fields': 'name,rating,formatted_address,photo,types',
            'key': API_KEY
        }
        try:
            response = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=params)
            data = response.json()
            if data.get('status') == 'OK':
                result = data.get('result', {})
                # Get photo reference if available
                photo_reference = result.get('photos', [{}])[0].get('photo_reference', None)
                if photo_reference:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={API_KEY}"
                else:
                    photo_url = None
                # Extract cuisine type from types
                cuisine_type = "Unknown"
                for t in result.get('types', []):
                    if t in SPECIFIC_CUISINE_TYPES:
                        cuisine_type = t.replace('_restaurant', '').title()
                        cuisine_set.add(cuisine_type)
                        break
                # Fallback: Infer from name
                if cuisine_type == "Unknown":
                    for cuisine in KNOWN_CUISINES:
                        if cuisine.lower() in result.get('name', '').lower():
                            cuisine_type = cuisine
                            cuisine_set.add(cuisine_type)
                            break
                enriched_favorites.append({
                    'name': result.get('name', 'N/A'),
                    'address': result.get('formatted_address', 'N/A'),
                    'rating': result.get('rating', 'N/A'),
                    'place_id': place_id,
                    'image_url': photo_url,
                    'cuisine_type': cuisine_type
                })
            else:
                logger.error(
                    f"Google Places API error for place_id={place_id}: "
                    f"status={data.get('status')}, error_message={data.get('error_message', '')}"
                )
                enriched_favorites.append({
                    'name': fav.name,
                    'address': fav.address,
                    'rating': fav.rating,
                    'place_id': place_id,
                    'image_url': None,
                    'cuisine_type': fav.cuisine_type
                })
        except Exception as e:
            logger.exception(f"Exception while fetching place details for place_id={place_id}: {e}")
            enriched_favorites.append({
                'name': fav.name,
                'address': fav.address,
                'rating': fav.rating,
                'place_id': place_id,
                'image_url': None,
                'cuisine_type': fav.cuisine_type
            })

    context = {
        'favorites': enriched_favorites,
        'cuisine_options': list(cuisine_set),  # Pass as a list instead of a concatenated string
    }
    return render(request, 'restaurants/favorites.html', context)


# Restaurant Detail View
def restaurant_detail(request, place_id):
    # Attempt to retrieve the Restaurant object from the database
    restaurant = Restaurant.objects.filter(place_id=place_id).first()
    if not restaurant:
        # Attempt to fetch restaurant details from Google Places API
        try:
            url = (
                f"https://maps.googleapis.com/maps/api/place/details/json?"
                f"place_id={place_id}&"
                f"fields=place_id,name,rating,formatted_address,geometry,types,formatted_phone_number,opening_hours,reviews&"
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
                reviews = details.get('reviews', [])  # Fetch Google Reviews

                # Extract cuisine type from types
                cuisine_type = "Unknown"
                for t in types:
                    if t in SPECIFIC_CUISINE_TYPES:
                        cuisine_type = t.replace('_restaurant', '').title()
                        break

                # Fallback: Infer from name
                if cuisine_type == "Unknown":
                    for cuisine in KNOWN_CUISINES:
                        if cuisine.lower() in name.lower():
                            cuisine_type = cuisine
                            break

                logger.debug(f"Extracted cuisine_type: {cuisine_type} for place_id: {place_id}")

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
        except Exception as e:
            logger.exception(f"Exception in restaurant_detail view for place_id={place_id}: {e}")
            return render(request, 'restaurants/restaurant_detail.html',
                          {'error': 'An error occurred while fetching details.', 'error_detail': str(e)})

    # At this point, we have the restaurant object
    try:
        # Fetch additional details using Google Places API to ensure latest information
        url = (
            f"https://maps.googleapis.com/maps/api/place/details/json?"
            f"place_id={place_id}&"
            f"fields=name,rating,formatted_address,geometry,rating,types,formatted_phone_number,opening_hours,reviews&"
            f"key={API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        if data.get('status') == 'OK':
            details = data.get('result', {})
            types = details.get('types', [])

            # Extract cuisine type from types
            updated_cuisine_type = restaurant.cuisine_type
            for t in types:
                if t in SPECIFIC_CUISINE_TYPES:
                    new_cuisine_type = t.replace('_restaurant', '').title()
                    if new_cuisine_type != updated_cuisine_type:
                        restaurant.cuisine_type = new_cuisine_type
                        updated_cuisine_type = new_cuisine_type
                        logger.debug(f"Updated cuisine_type to {new_cuisine_type} for restaurant: {restaurant}")
                        break

            # Fallback: Infer from name
            if updated_cuisine_type == "Unknown":
                for cuisine in KNOWN_CUISINES:
                    if cuisine.lower() in restaurant.name.lower():
                        restaurant.cuisine_type = cuisine
                        updated_cuisine_type = cuisine
                        logger.debug(f"Inferred cuisine_type to {cuisine} for restaurant: {restaurant}")
                        break

            # Update phone number if changed
            new_phone_number = details.get('formatted_phone_number', restaurant.formatted_phone_number)
            if new_phone_number != restaurant.formatted_phone_number:
                restaurant.formatted_phone_number = new_phone_number
                restaurant.save()
                logger.debug(f"Updated phone number to {new_phone_number} for restaurant: {restaurant}")

            # Fetch Google Reviews
            google_reviews = details.get('reviews', [])

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
                'google_reviews': google_reviews,  # Pass Google Reviews to the template
                'latitude': restaurant.latitude,  # Pass latitude
                'longitude': restaurant.longitude,  # Pass longitude
                'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,  # Pass API Key
                'place_id': place_id,
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
