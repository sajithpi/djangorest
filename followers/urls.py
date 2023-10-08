from django.urls import path
from .views import FollowUser, GetFollowData

urlpatterns = [
    path('user/followed_by',FollowUser.as_view(),name='follow'),
    path('user/followers-details',GetFollowData.as_view(),name='followers-details'), 
]