from django.urls import path
from . views import GoogleSocialAuthView, FacebookSocialAuthView

urlpatterns = [
    path('google-signup/', GoogleSocialAuthView.as_view(), name='google-signup'),
    path('facebook-signup/',FacebookSocialAuthView.as_view(), name='facebook-signup'),
]