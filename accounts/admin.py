from django.contrib import admin
from . models import User, UserProfile, CoverPhoto, Interest, DrinkChoice, Workout, Religion, FamilyPlanChoice, RelationShipGoal, SmokeChoice, EducationType, Language, ProfilePreference, Notification, UserTestimonial, Package, Order


class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username','gender','orientation','get_package_name','auth_provider','date_joined','has_2fa_enabled')
    list_filter = ('id','username')
    search_fields = ('id','username')
    
    def get_package_name(self, obj):
        return obj.package.name if obj.package else None

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','created_at','modified_at')
    list_filter = ('id','user',)
    search_fields = ('id','user')
    
class CoverPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_profile', 'created_at')
    list_filter = ('user_profile',)
    search_fields = ('user_profile__user__username', 'id')
    
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('name',)
    search_fields = ('name', 'id')
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','price','type','validity')
    list_filter = ('name',)
    search_fields = ('name', 'id')
    
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id','order_id','package_id','price','created_at','modified_at')
    list_filter = ('id', 'user_id','order_id')
    search_fields = ('id', 'user_id','order_id')
# Register your models here.
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    list_filter = ('name',)
    search_fields = ('name','id')
class ProfilePreferenceAdmin(admin.ModelAdmin):
    list_display = ('id','user_profile')
    list_filter = ('id','user_profile')
    search_fields = ('id','user_profile')
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('id','user','description','status')
    list_filter = ('id','user','description','status')
    search_fields = ('id','user','description','status')
    
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','from_user','to_user','type', 'description', 'user_has_seen', 'date_added')
    list_filter = ('from_user','to_user')
    search_fields = ('id','from_user','to_user')
    
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Order, OrdersAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(CoverPhoto, CoverPhotoAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(DrinkChoice, ChoiceAdmin)
admin.site.register(Workout, ChoiceAdmin)
admin.site.register(Religion, ChoiceAdmin)
admin.site.register(FamilyPlanChoice, ChoiceAdmin)
admin.site.register(RelationShipGoal, ChoiceAdmin)
admin.site.register(SmokeChoice, ChoiceAdmin)
admin.site.register(EducationType, ChoiceAdmin)
admin.site.register(Language, ChoiceAdmin)
admin.site.register(ProfilePreference, ProfilePreferenceAdmin)
admin.site.register(UserTestimonial, TestimonialAdmin)