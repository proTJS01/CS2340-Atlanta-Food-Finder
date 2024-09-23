from django.http import HttpResponse

def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    try:
        place_details = get_place_details(restaurant.google_place_id)
        context = {
            'restaurant': restaurant,
            'google_rating': place_details.get('rating', 'N/A'),
            'google_reviews': place_details.get('reviews', [])
        }
    except Exception as e:
        # Log the error
        print(f"Error fetching place details: {e}")
        return HttpResponse("Unable to fetch restaurant details at the moment.", status=500)

    return render(request, 'restaurants/restaurant_detail.html', context)