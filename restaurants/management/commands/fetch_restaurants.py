import requests
from django.core.management.base import BaseCommand
from restaurants.models import Restaurant

API_KEY = 'AIzaSyCP6CL_9cDOgF4bPxxHWD-o7sg0_BUEhFI'  # Replace with your actual API key
location = '33.7490,-84.3880'  # Example: Atlanta, GA (latitude, longitude)
radius = 5000  # 5km radius for searching nearby restaurants

class Command(BaseCommand):
    help = 'Fetch nearby restaurants using the Google Places API and store them in the database'

    def handle(self, *args, **kwargs):
        # Construct the Google Places API URL for nearby restaurant search
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&key={API_KEY}"

        # Make the API request
        response = requests.get(url)
        data = response.json()

        # Check for errors in the response
        if data.get('status') != 'OK':
            self.stdout.write(self.style.ERROR(f"Error fetching data: {data.get('error_message', 'Unknown error')}"))
            return

        # Loop through the results and add each restaurant to the database
        for place in data.get('results', []):
            name = place.get('name')
            latitude = place['geometry']['location']['lat']
            longitude = place['geometry']['location']['lng']
            address = place.get('vicinity', 'No address provided')
            place_id = place.get('place_id')

            # Create and store the restaurant in the database
            restaurant, created = Restaurant.objects.get_or_create(
                place_id=place_id,  # Ensure we don't duplicate restaurants
                defaults={
                    'name': name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': address,
                    'cuisine_type': "Unknown",  # You can update this field later
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added restaurant: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Restaurant {name} already exists"))
