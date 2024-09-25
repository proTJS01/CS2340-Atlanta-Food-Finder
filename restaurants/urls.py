# restaurants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),  # Favorites
    path('add_favorite/', views.add_favorite, name='add_favorite'),
    path('remove_favorite/<str:place_id>/', views.remove_favorite, name='remove_favorite'),
    path('restaurant/<str:place_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('map/', views.map_view, name='map'),  # Restaurant Search
]
