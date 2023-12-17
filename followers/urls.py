from django.urls import path
from .views import AddRemoveFavorite, GetFavoriteUsers, LikeDislike, GetLikeUsers, BLockUser, GetBlockedUsers, PokeUser, GetPokedUsers, RateUserCoverPhoto, ReportUsers

urlpatterns = [
    # Favorites
    path('user/add-remove-favorite',AddRemoveFavorite.as_view(),name='add-favorite'),
    path('user/get-favorite-list',GetFavoriteUsers.as_view(),name='get-favorite-details'), 

    # Like
    path('user/like-dislike-profile',LikeDislike.as_view(),name='like-dislike-profile'),
    path('user/get-like-users',GetLikeUsers.as_view(),name='get-like-users'),

    # Block
    path('user/block-unblock-user',BLockUser.as_view(),name='block-unblock-user'),
    path('user/get-blocked-users',GetBlockedUsers.as_view(),name='get-blocked-users'),

    # Report
    path('user/report-user',ReportUsers.as_view(),name='report-user'),


    # Poke
    path('user/poke-user',PokeUser.as_view(),name='poke-user'),
    path('user/get-poke-list',GetPokedUsers.as_view(),name='get-poke-list'),
    
    # Like
    path('user/rate-user-cover-photo',RateUserCoverPhoto.as_view(),name='rate-user-cover-photo'),
    # path('user/get-like-users',GetLikeUsers.as_view(),name='get-like-users'),

]