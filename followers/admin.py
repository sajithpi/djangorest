from django.contrib import admin
from . models import Favorite, Like, BlockedUser, Poke
# Register your models here.
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'favored_by')
    list_filter = ('user', 'favored_by')
    search_fields = ('user', 'favored_by')
    
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'liked_by')
    list_filter = ('user', 'liked_by')
    search_fields = ('user', 'liked_by')

class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','blocked_by')
    list_filter = ('user', 'blocked_by')
    search_fields = ('user', 'blocked_by')

class PokeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'poked_by')
    list_filter = ('user', 'poked_by')
    search_fields = ('user', 'poked_by')

admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(BlockedUser, BlockAdmin)
admin.site.register(Poke, PokeAdmin)