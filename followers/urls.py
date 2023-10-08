from django.urls import path
from .views import FollowUser

urlpatterns = [
    path('user/followed_by',FollowUser.as_view(),name='follow'),
]