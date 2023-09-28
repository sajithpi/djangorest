from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from . models import User, UserProfile, CoverPhoto

@receiver(post_save, sender = User)    
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user = instance)
        print("create the user profile")

    else:
        try:
            profile = UserProfile.objects.get(user = instance)
            profile.save()
            print("user is updated")
        except Exception as Error:
            #create the user profile if not exists
            UserProfile.objects.create(user = instance)
            print("profile is not exists so i created one")


@receiver(pre_save, sender = User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print(instance.username, 'this user is being saved')

@receiver(post_save, sender = UserProfile)
def post_save_create_cover_photo_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        CoverPhoto.objects.create(user_profile = instance)
        print("create the user cover")

    else:
        try:
            cover = CoverPhoto.objects.get(user_profile = instance)
            cover.save()
            print("user cover is updated")
        except Exception as Error:
            #create the user profile if not exists
            CoverPhoto.objects.create(user_profile = instance)
            print("user cover is not exists so i created one")
