To integrate Google Maps API into your Django project to satisfy the user stories related to searching and geolocation (User Story A and B), follow these steps:

Get API Key from Google Maps
 	- Go to the [Google Cloud Console](https://console.cloud.google.com/).
 - Create a new project (or use an existing one).
 	- Navigate to **APIs & Services > Library**, and search for **Maps JavaScript API**.
 - Enable it, then go to **APIs & Services > Credentials** to create an API key.

      2. Install Required Libraries
  
In your Django project, you may want to use a front-end JavaScript library to handle Google   Maps integration. You can simply use the standard Google Maps JavaScript API or a package like `django-google-maps` to make this easier for backend management if needed.

     pip install django-google-maps


      3. Set Up Django Models for Restaurants
   
To allow users to search for restaurants, you can set up a `Restaurant` model with fields such as name, cuisine type, address, latitude, longitude, etc. Django's model will store the restaurant data for use with the Google Maps API.

   Example models.py:

   from django.db import models
   from django_google_maps import fields as map_fields

   class Restaurant(models.Model):
       name = models.CharField(max_length=255)
       address = models.CharField(max_length=255)
       cuisine_type = models.CharField(max_length=100)
       latitude = map_fields.LatitudeField()
       longitude = map_fields.LongitudeField()
       # additional fields as necessary


4. Frontend: Add Google Maps JavaScript to Your Template
   
In the HTML template where you want to display the map, you can load the Google Maps JavaScript API and initialize the map using the user's geolocation (for search by location) and display markers for restaurants.

   Example `templates/map.html`:

   
   <!DOCTYPE html>
   <html>
   <head>
       <title>Restaurant Finder</title>
       <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap&libraries=places" async defer></script>
       <script>
           let map;
           function initMap() {
               map = new google.maps.Map(document.getElementById('map'), {
                   center: {lat: -34.397, lng: 150.644},  // Default center
                   zoom: 8
               });

               // Add marker for each restaurant
               const restaurants = JSON.parse(document.getElementById('restaurant-data').textContent);
               restaurants.forEach((restaurant) => {
                   const marker = new google.maps.Marker({
                       position: {lat: parseFloat(restaurant.latitude), lng: parseFloat(restaurant.longitude)},
                       map: map,
                       title: restaurant.name
                   });
               });
           }
       </script>
   </head>
   <body>
       <h1>Restaurant Finder</h1>
       <div id="map" style="height: 500px; width: 100%;"></div>

       <!-- Include data from the Django view (context variable) -->
       <script id="restaurant-data" type="application/json">{{ restaurant_data_json|safe }}</script>
   </body>
   </html>
  

 5. Views: Pass Restaurant Data to Template
 
In your `views.py`, query the restaurant data from the database and pass it to the template in JSON format.

   Example views.py:


   from django.shortcuts import render
   from .models import Restaurant
   import json

   def map_view(request):
       restaurants = Restaurant.objects.all()
       restaurant_data = [
           {
               'name': restaurant.name,
               'latitude': restaurant.latitude,
               'longitude': restaurant.longitude
           }
       for restaurant in restaurants]
       context = {'restaurant_data_json': json.dumps(restaurant_data)}
       return render(request, 'map.html', context)
   ```

6. Geolocation (User Story B)
   
To implement geolocation (for allowing users to view restaurants near them), you can use the browser's Geolocation API.

   Example addition to initMap():

 
   if (navigator.geolocation) {
       navigator.geolocation.getCurrentPosition((position) => {
           const userLocation = {
               lat: position.coords.latitude,
               lng: position.coords.longitude
           };
           map.setCenter(userLocation);

           // Optional: Add a marker for the user's location
           new google.maps.Marker({
               position: userLocation,
               map: map,
               title: 'You are here!'
           });
       });
   }
   ```

7. Restaurant Search (User Story B)
   
You can further enhance the search functionality by using the Google Places API for user-driven restaurant searches. For example, you could allow users to search for nearby restaurants based on their preferences such as cuisine type or rating.

### Additional Features
- **Restaurant Marker Popups**: Add `infoWindow` to each marker so that clicking on the marker will display more information about the restaurant.
- **Search Bar**: You can also implement a search bar that filters the markers based on user input like name, cuisine, or distance.

---

By following these steps, we can integrate the Google Maps API into our Django project and successfully meet the requirements for both User Authentication and Restaurant Search user stories from the class project.
