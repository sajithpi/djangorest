from django.contrib import admin
from . models import Favorite
# Register your models here.
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'favored_by')
    list_filter = ('user', 'favored_by')
    search_fields = ('user', 'favored_by')
    
admin.site.register(Favorite, FavoriteAdmin)