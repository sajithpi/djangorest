from django.db import models
from accounts.models import User, UserProfile
from django.conf import settings
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os

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
    
    def save(self, *args, **kwargs):
        # Set modified_at to current time in the timezone specified in settings
        self.modified_at = settings.NOW
        super().save(*args, **kwargs)
    

# class Chatroom(models.Model):
#     sender = models.CharField(max_length=55)
#     receiver = models.CharField(max_length=55)
    
class RoomChat(models.Model):
    receiver = models.CharField(max_length=1055)
    sender = models.CharField(max_length=1055)
    senderProfile = models.ForeignKey(UserProfile,on_delete=models.CASCADE, related_name="+")
    receiverProfile = models.ForeignKey(UserProfile,on_delete=models.CASCADE, related_name="+")
    encryption_key = models.BinaryField(null=True)

    def generate_key(self):
        # Generate a random 256-bit key for AES encryption
        key = os.urandom(32)
        return key
    

    def encrypt_content(self, plaintext, key):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        encoded_message = base64.b64encode(iv + ciphertext)
        return encoded_message.decode('utf-8')

    def decrypt_content(self, encoded_message, key):
        # Decode the base64-encoded ciphertext
        ciphertext = base64.b64decode(encoded_message)

        # Use the first 16 bytes of the ciphertext as the IV
        iv = ciphertext[:16]

        # Create the Cipher object with the specified IV
        cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=default_backend())

        # Decrypt the content
        decryptor = cipher.decryptor()
        decrypted_text = decryptor.update(ciphertext[16:]) + decryptor.finalize()

        return decrypted_text.decode('utf-8')
    def save(self, *args, **kwargs):
        # Generate key and encrypt content before saving
        if not self.encryption_key:
            key = self.generate_key()
            self.encryption_key = key

        super().save(*args, **kwargs)
class Connected(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="connected")
    room = models.ForeignKey(RoomChat, on_delete=models.CASCADE, related_name="connected")
    channel_name = models.CharField(max_length=100, null=False)
    connect_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
def stickers_upload_path(instance, filename):
    # Generate the upload path based on the user's ID
    return f'stickers/{filename}'
    
class Sticker(models.Model):
    photo = models.ImageField(upload_to=stickers_upload_path, blank = True, null = True)