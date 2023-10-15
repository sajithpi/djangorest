from django.urls import path
from .views import AddRemoveFavorite, GetFavoriteUsers, LikeDislike, GetLikeUsers

urlpatterns = [
    # Favorites
    path('user/add-remove-favorite',AddRemoveFavorite.as_view(),name='add-favorite'),
    path('user/get-favorite-list',GetFavoriteUsers.as_view(),name='get-favorite-details'), 

    # Like
    path('user/like-dislike-profile',LikeDislike.as_view(),name='like-dislike-profile'),
    path('user/get-like-users',GetLikeUsers.as_view(),name='get-like-users'), 
]