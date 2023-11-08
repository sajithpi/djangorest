from django.contrib import admin
from . models import TravelAim,MyTrip, TravelRequest
# Register your models here.

class TravelAimAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    list_filter = ('name',)
    search_fields = ('name','id')

class MyTripAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'travel_date', 'location', 'looking_for', 'days', 'description', 'status')
    list_filter = ('user', 'status')
    search_fields = ('user', 'status')

class TravelRequestAdmin(admin.ModelAdmin):
    list_display = ('id','trip_id','requested_user','description','status')
    list_filter = ('requested_user', 'trip_id', 'status')
    list_filter = ('requested_user', 'trip_id', 'status')


admin.site.register(TravelAim, TravelAimAdmin)
admin.site.register(MyTrip, MyTripAdmin)
admin.site.register(TravelRequest, TravelRequestAdmin)