from django.contrib import admin
from . models import User, UserProfile, CoverPhoto, Interest, DrinkChoice, Workouts, Religions, RelationShipGoals, SmokeChoices, EducationTypes


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
    
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(CoverPhoto, CoverPhotoAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(DrinkChoice, ChoiceAdmin)
admin.site.register(Workouts, ChoiceAdmin)
admin.site.register(Religions, ChoiceAdmin)
admin.site.register(RelationShipGoals, ChoiceAdmin)
admin.site.register(SmokeChoices, ChoiceAdmin)
admin.site.register(EducationTypes, ChoiceAdmin)