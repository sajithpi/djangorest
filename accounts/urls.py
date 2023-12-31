from django.urls import path, include
from .api import GetUserData, UpdateProfilePhoto, DeleteCoverPhoto, CheckUserExists, RemoveUserInterestView
from .views import RegisterView, RequestPasswordResetEmail, PasswordTokenCheckAPI, SetNewPasswordAPI, IntrestListCreateView
from rest_framework_simplejwt import views as jwt_views
urlpatterns = [
    path('api/getUser-data', GetUserData.as_view(), name='getUser-data'),
    path('api/upload-cover-photo', GetUserData.as_view(), name='upload-cover-photo'),
    path('api/delete-cover-photo', DeleteCoverPhoto.as_view(), name='delete-cover-photo'),
    path('api/get-interests', IntrestListCreateView.as_view(), name='get-interests'),
    path('api/check-email-exists', CheckUserExists.as_view(), name='check-email-exists'),
    path('api/update-profile-photo', UpdateProfilePhoto.as_view(), name='update-profile-photo'),
    path('api/remove_interest', RemoveUserInterestView.as_view(), name='remove-user-interest'),
    path('api/login', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('api/login/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
    path('api/register',RegisterView.as_view(), name="sign_up"),

    path('api/changePassword', RequestPasswordResetEmail.as_view(), name="change_password"),
    path('api/password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(),name='password_reset_confirm'),
    path('api/password-reset-complete',SetNewPasswordAPI.as_view(), name='password-reset-complete') 
    # path('forgot_password/', ForgotPassword.as_view(), name="forgot_password"),
    # path('reset_password_validate/<uidb64>/<token>', ResetPasswordValidate, name="reset_password_validate"),
    # path('reset_password', ResetPassword, name = 'forgot_password'),
]