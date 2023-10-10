from django.contrib import admin
from . models import User, UserProfile, CoverPhoto, Interest, DrinkChoice, Workout, Religion, RelationShipGoal, SmokeChoice, EducationType, Language, ProfilePreference


class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username')
    list_filter = ('id','username')
    search_fields = ('id','username')

class CoverPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_profile', 'created_at')
    list_filter = ('user_profile',)
    search_fields = ('user_profile__user__username', 'id')
    
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('name',)
    search_fields = ('name', 'id')
# Register your models here.
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    list_filter = ('name',)
    search_fields = ('name','id')
class ProfilePreferenceAdmin(admin.ModelAdmin):
    list_display = ('id','user_profile')
    list_filter = ('id','user_profile')
    search_fields = ('id','user_profile')
    
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(CoverPhoto, CoverPhotoAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(DrinkChoice, ChoiceAdmin)
admin.site.register(Workout, ChoiceAdmin)
admin.site.register(Religion, ChoiceAdmin)
admin.site.register(RelationShipGoal, ChoiceAdmin)
admin.site.register(SmokeChoice, ChoiceAdmin)
admin.site.register(EducationType, ChoiceAdmin)
admin.site.register(Language, ChoiceAdmin)
admin.site.register(ProfilePreference, ProfilePreferenceAdmin)