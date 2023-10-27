from django.urls import path, include
from .api import GetUserData, GetProfileDetails, UpdateProfilePhoto, UpdateUserLocation, DeleteCoverPhoto, CheckUserExists, RemoveUserInterestView, GetPreferences, UpdateProfilePreference, GetProfileMatches, Enable2FA, Test, GetNotifications, GetMyPreferences
from .views import RegisterView, RequestPasswordResetEmail, PasswordTokenCheckAPI, SetNewPasswordAPI, IntrestListCreateView, VerifyAccount, sendOTP, LogoutView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt import views as jwt_views
urlpatterns = [
    path('api/test',Test.as_view(), name='test'),
    path('api/getUser-data', GetUserData.as_view(), name='getUser-data'),
    path('api/get-profile-data', GetProfileDetails.as_view(), name='get-profile-data'),
    path('api/upload-cover-photo', GetUserData.as_view(), name='upload-cover-photo'),
    path('api/delete-cover-photo', DeleteCoverPhoto.as_view(), name='delete-cover-photo'),

    path('api/get-notifications', GetNotifications.as_view(), name='get-notifications'),
    
    path('api/get-interests', IntrestListCreateView.as_view(), name='get-interests'),
    path('api/get-preferences', GetPreferences.as_view(), name='get-preferences'),
    path('api/get-my-preferences',GetMyPreferences.as_view(), name='get-my-preferences'),
    path('api/update-profile-preference',UpdateProfilePreference.as_view(), name='update-profile-preference'),
    path('api/get-profile-matches',GetProfileMatches.as_view(), name='get-profile-matches'),
    path('api/update-my-location',UpdateUserLocation.as_view(), name='update-my-location'),

    path('api/check-email-exists', CheckUserExists.as_view(), name='check-email-exists'),
    path('api/update-profile-photo', UpdateProfilePhoto.as_view(), name='update-profile-photo'),
    path('api/remove_interest', RemoveUserInterestView.as_view(), name='remove-user-interest'),
    # path('api/login', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('api/login', jwt_views.TokenObtainPairView.as_view(serializer_class = CustomTokenObtainPairSerializer), name ='token_obtain_pair'),
    path('api/login/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
    path('api/logout',LogoutView.as_view(),name='logout'),
    path('api/register',RegisterView.as_view(), name="sign_up"),
    path('api/verify-account',VerifyAccount.as_view(), name='verify-account'), #Verify Login/ Register

    path('api/changePassword', RequestPasswordResetEmail.as_view(), name="change_password"),
    path('api/password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(),name='password_reset_confirm'),
    path('api/password-reset-complete',SetNewPasswordAPI.as_view(), name='password-reset-complete'), 
    path('api/send-otp',sendOTP.as_view(), name='send-otp'),
    path('api/enable-2fa',Enable2FA.as_view(), name='enable-2fa'),
    
    path('api/follow/',include('followers.urls')),
]