# CS2340App/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('', include('restaurants.urls')),  # Includes home, map, profile, etc.
]
