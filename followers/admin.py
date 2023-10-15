from django.contrib import admin
from . models import Favorite, Like
# Register your models here.
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'favored_by')
    list_filter = ('user', 'favored_by')
    search_fields = ('user', 'favored_by')
    
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'liked_by')
    list_filter = ('user', 'liked_by')
    search_fields = ('user', 'liked_by')
    
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Like, LikeAdmin)