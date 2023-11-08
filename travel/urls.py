from django.urls import include, path
from . views import TravelLookingFor, TravelPlan, RequestTrip, ListTrips
urlpatterns = [
    path('get-travel-aims',TravelLookingFor.as_view(),name="get-travel-aims"),
    
    path('my-trip',TravelPlan.as_view(), name='my-trip'),
    path('request-trip', RequestTrip.as_view(), name='request-trip'),
    path('list-trips',ListTrips.as_view(), name='list-trips')
]