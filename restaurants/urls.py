# restaurants/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Changed from home_view to home
    path('map/', views.map_view, name='map'),
    path('profile/', views.profile, name='profile'),  # Changed from profile_view to profile
    path('register/', views.register, name='register'),  # Changed from register_view to register
    path('favorites/', views.favorites, name='favorites'),
    path('add_favorite/', views.add_favorite, name='add_favorite'),
    path('remove_favorite/<str:place_id>/', views.remove_favorite, name='remove_favorite'),
    path('restaurant/<str:place_id>/', views.restaurant_detail, name='restaurant_detail'),  # Added restaurant_detail URL
    # Add other URLs as needed
]
