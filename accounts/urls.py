from django.urls import path, include
from .api import GetUserData, GetProfileDetails, getLoginUserData,PackageListView, UpdateProfilePhoto, UpdateUserLocation, DeleteCoverPhoto, CheckUserExists, RemoveUserInterestView, GetPreferences, UpdateProfilePreference, GetProfileMatches, Enable2FA, Test, UserNotifications, GetMyPreferences, GetClientId, UploadKYC, MlmRegister
from .views import RegisterView, RequestPasswordResetEmail, PasswordTokenCheckAPI, SetNewPasswordAPI, IntrestListCreateView, VerifyAccount, sendOTP, LogoutView, Testimonial, PasswordReset, GetTestimonialsView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt import views as jwt_views
from . paypal import PayPalPaymentView, CaptureOrderView
urlpatterns = [
    path('api/test',Test.as_view(), name='test'),
    path('api/getUser-data', GetUserData.as_view(), name='getUser-data'),
    path('api/get-profile-data', GetProfileDetails.as_view(), name='get-profile-data'),
    path('api/get-login-user-data',getLoginUserData.as_view(), name='get-login-user-data'),
    path('api/upload-cover-photo', GetUserData.as_view(), name='upload-cover-photo'),
    path('api/delete-cover-photo', DeleteCoverPhoto.as_view(), name='delete-cover-photo'),

    path('api/user-notifications', UserNotifications.as_view(), name='get-notifications'),
   

    
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
    path('api/reset-password',PasswordReset.as_view(), name='reset-password'),

    path('api/changePassword', RequestPasswordResetEmail.as_view(), name="change_password"),
    path('api/password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(),name='password_reset_confirm'),
    path('api/password-reset-complete',SetNewPasswordAPI.as_view(), name='password-reset-complete'), 
    path('api/send-otp',sendOTP.as_view(), name='send-otp'),
    path('api/enable-2fa',Enable2FA.as_view(), name='enable-2fa'),
    
    path('api/follow/',include('followers.urls')),
    path('api/social-auth/',include('social_auth.urls')),
    path('api/travel/', include('travel.urls')),
    path('api/chat/',include('chat.urls')),
    
    
    path('api/paypal-create-order', PayPalPaymentView.as_view(), name="paypal-create-order"),
    path('api/paypal-capture-order', CaptureOrderView.as_view(), name="paypal-capture-order"),
    path('api/get-client-id',GetClientId.as_view(), name='get-client-id'),
    path('api/user-testimonial',Testimonial.as_view(), name='testimonial'),
    
    path('api/get-testimonials',GetTestimonialsView.as_view(), name='get-testimonials'),
    
    path('api/packages', PackageListView.as_view(), name='package-list-create'),
    
    path('api/upload-kyc',UploadKYC.as_view(), name='upload-kyc'),
    
    path('api/register-mlm',MlmRegister.as_view(), name='register-mlm'),

]