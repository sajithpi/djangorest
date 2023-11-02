from django.urls import include, path
from . views import TravelLookingFor, TravelPlan, RequestTrip
urlpatterns = [
    path('get-travel-aims',TravelLookingFor.as_view(),name="get-travel-aims"),
    path('plan-trip',TravelPlan.as_view(), name='plan-trip'),
    path('request-trip', RequestTrip.as_view(), name='request-trip'),
]