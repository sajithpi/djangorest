from django.contrib import admin
from . models import User, UserProfile, CoverPhoto, Interest


class CoverPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_profile', 'created_at')
    list_filter = ('user_profile',)
    search_fields = ('user_profile__user__username', 'id')
    
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('name',)
    search_fields = ('name', 'id')
# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(CoverPhoto, CoverPhotoAdmin)
admin.site.register(Interest, InterestAdmin)