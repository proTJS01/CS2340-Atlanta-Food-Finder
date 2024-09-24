from django.contrib import admin
from .models import Restaurant, Favorite, Review

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine_type', 'address', 'latitude', 'longitude', 'place_id')
    search_fields = ('name', 'cuisine_type', 'address', 'place_id')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'place_id', 'address', 'rating', 'created_at')
    search_fields = ('name', 'user__username', 'place_id', 'address')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'rating', 'created_at')
    search_fields = ('user__username', 'restaurant__name')
    list_filter = ('rating', 'created_at')
