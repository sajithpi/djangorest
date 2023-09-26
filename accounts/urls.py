from django.urls import path, include
from .api import SimpleApI
from .views import RegisterView
from rest_framework_simplejwt import views as jwt_views
urlpatterns = [
    path('api/hello', SimpleApI.as_view() ),
    path('api/login/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('api/login/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
    path('api/register',RegisterView.as_view(), name="sign_up")
]