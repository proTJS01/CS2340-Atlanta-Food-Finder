from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # Ratings 1-5

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label="Rating (1-5)"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Your Review"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
