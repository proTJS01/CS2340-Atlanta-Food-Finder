# restaurants/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('map/', views.map_view, name='map'),  # Restaurant search
    # path('profile/', views.profile, name='profile'),  # Removed profile URL
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Login
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout
    path('accounts/signup/', views.signup, name='signup'),  # Corrected Name
    path('favorites/', views.favorites, name='favorites'),  # Favorites page
    path('add_favorite/', views.add_favorite, name='add_favorite'),  # Add favorite
    path('remove_favorite/<str:place_id>/', views.remove_favorite, name='remove_favorite'),  # Remove favorite
    path('restaurant/<str:place_id>/', views.restaurant_detail, name='restaurant_detail'),  # Restaurant detail

    # Password Reset URLs
    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
