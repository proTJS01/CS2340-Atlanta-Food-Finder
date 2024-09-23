from django.urls import path, include
from restaurant import views


urlpatterns = [
    path('add-to-favorites/<int:restaurant_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('profile/', views.profile, name='profile'),
    path('', views.profile, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
]
