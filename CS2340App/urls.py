from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('map/', include('restaurants.urls')),  # This should point to your app's URLs
]