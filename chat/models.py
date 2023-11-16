from django.db import models
from accounts.models import User, UserProfile


def user_profile_picture_upload_path(instance, filename):
    # Generate the upload path based on the user's ID
    return f'chatroom/{instance.room.id}/message_photos/{filename}'

# Create your models here.

class Chat(models.Model):
    count = 0

    content = models.CharField(max_length=1555,null=True)
    photo = models.ImageField(upload_to=user_profile_picture_upload_path, blank = True, null = True)
    timestamp = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="+")
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="+")
    room = models.ForeignKey('RoomChat',on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def Counter(self):
        self.count += 1
        return self.count
    

# class Chatroom(models.Model):
#     sender = models.CharField(max_length=55)
#     receiver = models.CharField(max_length=55)
    
class RoomChat(models.Model):
    receiver = models.CharField(max_length=1055)
    sender = models.CharField(max_length=1055)
    senderProfile = models.ForeignKey(UserProfile,on_delete=models.CASCADE, related_name="+")
    receiverProfile = models.ForeignKey(UserProfile,on_delete=models.CASCADE, related_name="+")
    

class Connected(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="connected")
    room = models.ForeignKey(RoomChat, on_delete=models.CASCADE, related_name="connected")
    channel_name = models.CharField(max_length=100, null=False)
    connect_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username