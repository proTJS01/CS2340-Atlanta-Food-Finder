import googlemaps

GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY'
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_place_details(place_id):
    place_details = gmaps.place(place_id, fields=['name', 'rating', 'reviews'])
    return place_details['result']