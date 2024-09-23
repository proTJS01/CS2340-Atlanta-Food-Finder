from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Restaurant, Favorite

@login_required
def add_to_favorites(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
    return redirect('profile')

@login_required
def profile(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'restaurant/profile.html', {'favorites': favorites})

