from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('map/', include('restaurants.urls')),  # Restaurants app URLs
    path('', include('restaurants.urls')),  # Make map the homepage
]
