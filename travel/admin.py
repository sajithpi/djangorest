from django.contrib import admin
from . models import TravelAim
# Register your models here.

# class TravelAimAdmin(admin.ModelAdmin):
#     list_display = ('id','name')
#     list_filter = ('name',)
#     search_fields = ('name','id')
    
admin.site.register(TravelAim)