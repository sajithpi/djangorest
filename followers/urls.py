from django.urls import path
from .views import AddRemoveFavorite, GetFavoriteUsers

urlpatterns = [
    path('user/add-remove-favorite',AddRemoveFavorite.as_view(),name='add-favorite'),
    path('user/get-favorite-list',GetFavoriteUsers.as_view(),name='get-favorite-details'), 
]