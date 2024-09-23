from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map-view'),  # Use an empty string so it's just /map/ without another /map/
]