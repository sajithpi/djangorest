from django.contrib import admin
from . models import Follower
# Register your models here.
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'followed_by', 'following')
    list_filter = ('followed_by', 'following')
    search_fields = ('followed_by', 'following')
    
admin.site.register(Follower, FollowerAdmin)