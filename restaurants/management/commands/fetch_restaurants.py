import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from restaurants.models import Restaurant

API_KEY = settings.GOOGLE_MAPS_API_KEY  # Fetch API key from settings
location = '33.7490,-84.3880'  # Example: Atlanta, GA (latitude, longitude)
radius = 5000  # 5km radius for searching nearby restaurants
base_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&key={API_KEY}"

class Command(BaseCommand):
    help = 'Fetch nearby restaurants using the Google Places API and store them in the database'

    def handle(self, *args, **kwargs):
        # Fetch places from the API with pagination
        self.fetch_places(base_url)

    def fetch_places(self, url):
        while url:
            # Make the API request
            response = requests.get(url)
            data = response.json()

            # Check for errors in the response
            if data.get('status') != 'OK':
                self.stdout.write(self.style.ERROR(f"Error fetching data: {data.get('error_message', 'Unknown error')}"))
                return

            # Loop through the results and add each restaurant to the database
            for place in data.get('results', []):
                name = place.get('name', 'Unknown')
                latitude = place.get('geometry', {}).get('location', {}).get('lat', 0.0)
                longitude = place.get('geometry', {}).get('location', {}).get('lng', 0.0)
                address = place.get('vicinity', 'No address provided')
                place_id = place.get('place_id', None)

                if place_id:
                    # Extract cuisine type from types
                    types = place.get('types', [])
                    cuisine_keywords = ['restaurant', 'cafe', 'bar', 'bistro', 'diner', 'eatery', 'pub']
                    cuisine_type = next((t.replace('_', ' ').title() for t in types if t not in cuisine_keywords), "Unknown")

                    # Create and store the restaurant in the database
                    restaurant, created = Restaurant.objects.get_or_create(
                        place_id=place_id,  # Ensure we don't duplicate restaurants
                        defaults={
                            'name': name,
                            'latitude': latitude,
                            'longitude': longitude,
                            'address': address,
                            'cuisine_type': cuisine_type,  # Extracted from types
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added restaurant: {name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Restaurant {name} already exists"))

            # Check for pagination token
            next_page_token = data.get('next_page_token')
            if next_page_token:
                time.sleep(2)  # Required delay for pagination
                url = f"{base_url}&pagetoken={next_page_token}"
            else:
                url = None
